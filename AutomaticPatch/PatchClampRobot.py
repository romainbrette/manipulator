from threading import Thread
from Autofocus import *
from Camera import *
from Amplifier import *
from Pressure_controller import *
import numpy as np
import cv2
from math import fabs
import time
import os
import errno
import trackpy as tp

__all__ = ['PatchClampRobot']


class PatchClampRobot(Thread):
    """
    Class to control devices for patch clamp.
    """

    def __init__(self, controller, arm, camera, amplifier=None, pump=None, verbose=True):

        # Thread init
        Thread.__init__(self)

        # Devices
        self.dev, self.microscope, self.arm = init_device(controller, arm)
        self.controller = controller

        # Tab for template images
        self.template = []

        # Boolean for calibrated state
        self.calibrated = 0

        # Maximum distance from initial position allowed during calibration
        self.maxdist = 2000

        # Initial displacement of the arm during autocalibration, in um
        self.first_step = 2.
        self.step = 0

        # Rotational matrix of the platform compared to the camera - to be calibrated
        self.rot = np.matrix([[0., 0., 0.], [0., 0., 0.], [0., 0., 1.]])
        self.rot_inv = np.matrix([[0., 0., 0.], [0., 0., 0.], [0., 0., 1.]])

        # Initializing transformation matrix (Jacobian) between the platform and the tip
        self.mat = np.matrix([[0., 0., 0.], [0., 0., 0.], [0., 0., 0.]])
        self.inv_mat = np.matrix([[0., 0., 0.], [0., 0., 0.], [0., 0., 0.]])

        # Initial position of the tip in the image, before calibration
        self.x_init, self.y_init = 0, 0

        # Ratio um/pixel of the camera
        self.um_px = 0.

        # Position of the tip in the template image
        self.template_loc = [0., 0.]

        # Withdraw direction - changed at end of calibration
        self.withdraw_sign = 0

        # Resistance of pipette
        self.pipette_resistance = 0.
        self.pipette_resistance_checked = False

        # Messages
        self.verbose = verbose
        self.message = ''

        # Connected devices
        self.amplifier = ResistanceMeter(amplifier)
        if not self.amplifier.connected:
            self.update_message('Failed to connect to {}, switching to Fake Amplifier.'.format(amplifier))
        self.pressure = PressureController(pump)
        if not self.pressure.connected:
            self.update_message('Failed to connect to {}, switching to Fake Pump.'.format(pump))
        self.cam = Camera(camera, self.click_event, self.img_func)

        # Patch Clamp variables
        self.enable_clamp = False

        # Event on camera window
        self.event = {'event': None, 'x': self.cam.width/2, 'y': self.cam.height/2}
        self.following = False
        self.offset = 0.
        self.follow_paramecia = False
        self.disp_img_func = False
        self.xt, self.yt = 0, 0

        # Start the thread run
        self.running = True
        self.start()

        pass

    def run(self):
        """
        Thread run. Used to handle manipulator commands after a mouse callback on the camera's window and
         autocalibration process while refreshing the dispayed image.
        """
        while (not self.calibrated) & self.running:
            # Robot has not been calibrated, wait for calibration
            if self.event['event'] == 'Calibration':
                # Auto calibration
                _ = self.calibrate()
                self.event['event'] = None

        while self.calibrated & self.running:

            if self.follow_paramecia:

                diameter = 11
                img = self.cam.frame
                height, width = img.shape[:2]
                ratio = width / 256
                #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                img = cv2.resize(img, (width/ratio, height/ratio))  # faster
                gauss = cv2.GaussianBlur(img, (9, 9), 0)
                canny = cv2.Canny(gauss, img.shape[0]/8, img.shape[0]/8)
                ret, thresh = cv2.threshold(canny, 127, 255, 0)
                im2, contours, hierarchy = cv2.findContours(thresh, 1, 2)
                for cnt in contours:
                    try:
                        M = cv2.moments(cnt)
                        if bool(cv2.arcLength(cnt, True)) & bool(M['m00']):
                            (x, y), radius = cv2.minEnclosingCircle(cnt)
                            cx = int(M['m10'] / M['m00'])
                            cy = int(M['m01'] / M['m00'])
                            center = (cx, cy)
                            radius = int(radius)
                            if (radius < 55) & (radius > 15):
                                if ((cx - lastX)**2+(cy-lastY)**2)**0.5 < 30 :
                                    lastX = cx
                                    lastY = cy
                                    target = self.rot_inv * np.array([[(width / 2 - cx*ratio) * self.um_px * 0.35],
                                                                      [(height / 2 - cy*ratio) * self.um_px * 0.35],
                                                                      [0]])
                                    self.microscope.absolute_move_group(
                                        np.transpose(self.microscope.position()) + target,
                                        [0, 1, 2])
                                    break
                    except cv2.error:
                        pass
                '''
                f = tp.locate(canny, diameter, invert=False, noise_size=1, minmass=300, max_iterations=1,
                              characterize=True, engine='python')  # numba is too slow!
                xp = np.array(f['x'])
                yp = np.array(f['y'])

                # Closest one
                if len(xp) > 0:
                    self.disp_img_func = True
                    j = np.argmin((xp - width / 40) ** 2 + (yp - height / 40) ** 2)
                    xt, yt = xp[j], yp[j]
                    xt = int(xt)
                    yt = int(yt)
                    cv2.circle(canny, (xt, yt), 5, (255, 0, 0), 1)
                    cv2.imshow('Tracking', canny)
                    cv2.waitKey(1)
                    xt *= 20
                    yt *= 20
                    self.xt, self.yt = xt, yt
                    target = self.rot_inv * np.array([[(width / 2 - xt) * self.um_px*0.35],
                                                      [(height / 2 - yt) * self.um_px*0.35],
                                                      [0]])
                    self.microscope.absolute_move_group(np.transpose(self.microscope.position()) + target,
                                                        [0, 1, 2])

                else:
                    self.disp_img_func = False
                '''
            else:
                # Robot has been calibrated, positionning is possible
                if self.event['event'] == 'Positioning':

                    # Move the tip of the pipette to the clicked position
                    self.following = False
                    self.update_message('Moving...')

                    # Getting the position of the tip and the micriscope
                    pos = np.transpose(self.microscope.position())

                    # Computing the desired position
                    offset = self.rot_inv*np.array([[(self.x_init - (self.event['x'] - self.template_loc[0])) * self.um_px],
                                                    [(self.y_init - (self.event['y'] - self.template_loc[1])) * self.um_px],
                                                    [0]])
                    pos += offset

                    # Moving the tip after a withdraw for security
                    self.arm.relative_move(self.withdraw_sign*10, 0)
                    self.arm.wait_motor_stop(0)
                    self.arm.absolute_move_group(self.inv_mat*pos, [0, 1, 2])

                    # Event is finished
                    self.event['event'] = None
                    self.update_message('done.')

                elif (self.event['event'] == 'PatchClamp') & self.pipette_resistance_checked:

                    self.following = False
                    # Patch (and Clamp) at the clicked position
                    self.update_message('Moving...')

                    # Getting desired position
                    mic_pos = np.transpose(self.microscope.position())

                    offset = self.rot_inv*np.array([[(self.x_init - (self.event['x'] - self.template_loc[0])) * self.um_px],
                                                    [(self.y_init - (self.event['y'] - self.template_loc[1])) * self.um_px],
                                                    [0]])
                    mic_pos += offset
                    tip_pos = self.mat*np.transpose(self.arm.position())

                    # Withdraw the pipette for security
                    if self.withdraw_sign*np.sign(self.mat[2, 0])*(tip_pos[2, 0] - mic_pos[2, 0]) < 0:
                        # tip is lower than the desired position, withdraw to the desired heigth
                        move = self.withdraw_sign*(abs(mic_pos[2, 0]-tip_pos[2, 0])+15)/abs(self.mat[2, 0])
                    else:
                        # tip is higher than, or at, desired height
                        move = self.withdraw_sign*15/abs(self.mat[2, 0])

                    # Applying withdraw
                    self.arm.relative_move(move, 0)
                    self.arm.wait_motor_stop([0])

                    # From now, use theoretical position rather than true position to compensate for unreachable position
                    # Computing supposed position of the tip.
                    theorical_tip_pos = tip_pos + self.mat*np.array([[move], [0], [0]])

                    # Computing intermediate position in the same horizontal plan as the supposed tip position
                    # Only x axis should have an offset compared to the desired position
                    intermediate_x_pos = self.withdraw_sign*abs(theorical_tip_pos[2, 0]-mic_pos[2, 0])/abs(self.mat[2, 0])
                    intermediate_pos = mic_pos + self.mat*np.array([[intermediate_x_pos], [0], [0]])

                    # Applying moves to intermediate position
                    self.arm.absolute_move_group(self.inv_mat*intermediate_pos, [0, 1, 2])
                    self.arm.wait_motor_stop([0, 1, 2])

                    # Getting close to the desired postion (offset 10um on x axis)
                    self.linear_move(intermediate_pos, mic_pos+self.mat*np.array([[self.withdraw_sign*10.], [0.], [0.]]))
                    self.arm.wait_motor_stop([0, 1, 2])

                    if abs(self.pipette_resistance-self.get_resistance()) < 1e6:
                        # Pipette has not been obstructed during previous moves, updating pipette offset
                        self.pressure.release()
                        self.amplifier.auto_pipette_offset()
                        time.sleep(2)
                        if self.patch(mic_pos):
                            # Patch successful
                            if self.enable_clamp:
                                # Clamp is enabled, clamping
                                time.sleep(120)
                                self.clamp()
                    else:
                        # Pipette has been obstructed
                        self.update_message('ERROR: pipette is obstructed.')

                    # Envent is finished
                    self.event['event'] = None

                elif self.following & (not self.event['event']):
                    # The tip follow the camera
                    # Same as poistionning, but without updating events at the end
                    pos = np.transpose(self.microscope.position())
                    # tip_pos = self.mat * np.transpose(self.arm.position())

                    offset = self.rot_inv*np.array([[(self.x_init - (self.event['x'] - self.template_loc[0])) * self.um_px],
                                                    [(self.y_init - (self.event['y'] - self.template_loc[1])) * self.um_px],
                                                    [self.withdraw_sign*np.sign(self.mat[2, 0])*self.offset]])
                    pos = pos + offset
                    self.arm.absolute_move_group(self.inv_mat*pos, [0, 1, 2])
        pass

    def img_func(self, img):
        if self.disp_img_func & self.follow_paramecia:
            cv2.circle(img, (self.xt, self.yt), 5, (255, 0, 0), 1)

    def go_to_zero(self):
        """
        Make the arm and platform go to the origin: state before the calibration
        """

        self.arm.go_to_zero([0, 1, 2])
        self.microscope.go_to_zero([0, 1, 2])
        self.arm.wait_motor_stop([0, 1, 2])
        self.microscope.wait_motor_stop([0, 1, 2])
        time.sleep(.2)
        pass

    def calibrate_platform(self):
        """
        Calibrate the platform:
        Set zero position as current position
        Compute rotational matrix between the platform and camera 
        """

        # Get a series of template images for auto focus
        self.get_template_series(11)

        # Saving initial position of the tip on the screen
        _, _, loc = templatematching(self.cam.frame, self.template[len(self.template) // 2])
        self.x_init, self.y_init = loc[:2]

        # Getting the rotation matrix between the platform and the camera
        for i in range(2):

            # Moving the microscope
            self.microscope.relative_move(120, i)
            self.microscope.wait_motor_stop(i)
            time.sleep(.5)

            # Getting the displacement, in pixels, of the tip on the screen
            _, _, loc = templatematching(self.cam.frame, self.template[len(self.template) // 2])
            dx = loc[0] - self.x_init
            dy = loc[1] - self.y_init

            # Determination of um_px
            dist = (dx ** 2 + dy ** 2) ** 0.5
            self.um_px = self.microscope.position(i) / dist

            # Compute the rotational matrix
            self.rot[0, i] = dx / dist
            self.rot[1, i] = dy / dist

            # Resetting position of microscope
            self.microscope.go_to_zero([i])

        # Inverse rotation matrix for future use
        self.rot_inv = np.linalg.inv(self.rot)
        pass

    def calibrate_arm(self, axis):
        """
        Calibrate the arm along given axis.
        :param axis: axis to calibrate
        :return: 0 if calibration failed, 1 otherwise
        """

        while self.arm.position(axis) < self.maxdist:

            # calibrate arm axis using exponential moves:
            # moves the arm, recenter the tip and refocus.
            try:
                self.exp_focus_track(axis)
            except EnvironmentError:
                self.update_message('Could not track the tip.')
                return 0

        # When calibration is finished:

        # Resetting position of arm and microscope so no error gets to the next axis calibration
        self.go_to_zero()
        time.sleep(2)

        return 1

    def exp_focus_track(self, axis):
        """
        Focus after an arm move along given axis
        """

        # Update step distance
        if self.arm.position(axis) == 0:
            self.step = self.first_step
        elif self.arm.position(axis)+self.step*2 > self.maxdist:
            self.step = self.maxdist-self.arm.position(axis)
        else:
            self.step *= 2.

        # Move the arm
        self.arm.step_move(self.step, axis)

        # Move the platform to center the tip
        for i in range(3):
            self.microscope.step_move(self.mat[i, axis] * self.step, i)

        # Waiting for motors to stop
        self.arm.wait_motor_stop(axis)
        self.microscope.wait_motor_stop([0, 1, 2])

        # Focus around the estimated focus height
        try:
            _, _, loc = self.focus()
        except ValueError:
            raise EnvironmentError('Could not focus on the tip')

        # Move the platform for compensation
        delta = np.array([[(self.x_init - loc[0]) * self.um_px], [(self.y_init - loc[1]) * self.um_px], [0]])
        move = self.rot_inv * delta
        for i in range(2):
            self.microscope.step_move(move[i, 0], i)

        self.microscope.wait_motor_stop([0, 1])

        # Update the transform matrix
        for i in range(3):
            self.mat[i, axis] = self.microscope.position(i) / self.arm.position(axis)

        pass

    def get_withdraw_sign(self):
        """
        Compute the sign for withdraw moves
        """
        if fabs(self.mat[0, 0] / self.mat[1, 0]) > 1:
            i = 0
        else:
            i = 1
        if (self.template_loc[i] != 0) ^ ((self.mat[i, 0] > 0) ^ (self.rot[i, 0] > 0)):
            self.withdraw_sign = 1
        else:
            self.withdraw_sign = -1
        pass

    def calibrate(self):
        """
        Calibrate the entire Robot
        :return: 0 if calibration failed, 1 otherwise
        """

        self.update_message('Calibrating platform...')

        self.calibrate_platform()

        self.update_message('Platform Calibrated.')

        # calibrate arm x axis
        self.update_message('Calibrating x axis...')
        calibrated = self.calibrate_arm(0)

        if not calibrated:
            self.update_message('ERROR: Could not calibrate x axis.')
            return 0
        else:
            self.update_message('x axis calibrated.')

        # calibrate arm y axis
        self.update_message('Calibrating y axis...')
        calibrated = self.calibrate_arm(1)

        if not calibrated:
            self.update_message('ERROR: Could not calibrate y axis.')
            return 0
        else:
            self.update_message('y axis calibrated.')

        # calibrate arm z axis
        self.update_message('Calibrating z axis...')
        calibrated = self.calibrate_arm(2)

        if not calibrated:
            self.update_message('ERROR: Could not calibrate z axis.')
            return 0
        else:
            self.update_message('z axis calibrated.\n'
                                'Autocalibration done.\n'
                                'Accuracy: {}'.format(self.matrix_accuracy()))

        # Getting the direction to withdraw pipette along x axis
        self.get_withdraw_sign()
        self.inv_mat = np.linalg.inv(self.mat)
        self.calibrated = 1
        self.cam.click_on_window = True
        self.save_calibration()
        return 1

    def save_calibration(self):
        """
        Save calibration in text files
        """

        path = './{}/'.format(self.controller)
        # Check if path exist, if not, creates it.
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as exc:
                # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        # Save Jacobian matrix (self.mat)
        with open("./{i}/mat.txt".format(i=self.controller), 'wt') as f:
            for i in range(3):
                f.write('{a},{b},{c}\n'.format(a=self.mat[i, 0], b=self.mat[i, 1], c=self.mat[i, 2]))

        # Save rotational matrix
        with open("./{i}/rotmat.txt".format(i=self.controller), 'wt') as f:
            for i in range(3):
                f.write('{a},{b},{c}\n'.format(a=self.rot[i, 0], b=self.rot[i, 1], c=self.rot[i, 2]))

        # Save other data
        with open('./{i}/data.txt'.format(i=self.controller), 'wt') as f:
            f.write('{d}\n'.format(d=self.um_px))
            f.write('{d}\n'.format(d=self.x_init))
            f.write('{d}\n'.format(d=self.y_init))
            f.write('{d}\n'.format(d=self.template_loc[0]))
            f.write('{d}\n'.format(d=self.template_loc[1]))

    def load_calibration(self):
        """
        Load a calibration
        :return: 
        """
        try:
            with open("./{i}/mat.txt".format(i=self.controller), 'rt') as f:
                i = 0
                for line in f:
                    line = line.split(',')
                    for j in range(3):
                        self.mat[i, j] = float(line[j])
                    i += 1
                self.inv_mat = np.linalg.inv(self.mat)

            with open("./{i}/rotmat.txt".format(i=self.controller), 'rt') as f:
                i = 0
                for line in f:
                    line = line.split(',')
                    for j in range(3):
                        self.rot[i, j] = float(line[j])
                    i += 1
                self.rot_inv = np.linalg.inv(self.rot)

            with open('./{i}/data.txt'.format(i=self.controller), 'rt') as f:
                self.um_px = float(f.readline())
                self.x_init = float(f.readline())
                self.y_init = float(f.readline())
                self.template_loc[0] = float(f.readline())
                self.template_loc[1] = float(f.readline())

            self.get_withdraw_sign()
            self.arm.set_to_zero([0, 1, 2])
            self.microscope.set_to_zero([0, 1, 2])
            self.calibrated = 1
            self.cam.click_on_window = True
            self.update_message('Calibration loaded.')
            return 1

        except IOError:
            # Files do not exist
            self.update_message('ERROR: {i} has not been calibrated.'.format(i=self.controller))
            return 0

    def click_event(self, event, x, y, flags, param):
        """
        Update the event variable after a click on the window.
        Shall be used along cv2.setMouseCallback
        :param event: Type of mouse interaction with the window (auto) 
        :param x: position x of the event (auto)
        :param y: position y of the event (auto)
        :param flags: extra flags (auto)
        :param param: extra parameters (auto)
        :return: 
        """
        del flags, param
        if self.calibrated:
            if event == cv2.EVENT_LBUTTONUP:
                # Left click
                self.event = {'event': 'Positioning', 'x': x, 'y': y}

            elif event == cv2.EVENT_RBUTTONUP:
                # Right click
                self.event = {'event': 'PatchClamp', 'x': x, 'y': y}
        pass

    def enable_click_position(self):
        cv2.setMouseCallback(self.cam.winname, self.click_event)
        pass

    def linear_move(self, initial_position, final_position):
        """
        Goes to an absolute position in straight line.
        The initial position can be hypothetical (to auto correct motors limit) or true current position
        :param initial_position: absolute position to begin the movement with. (ndarray)
        :param final_position: absolute position to go. (ndarray)
        :return: none
        """
        if any(initial_position - final_position):
            # The desired position is not the actual position (would make a 'divide by zero' error otherwise)

            # Compute directional vector
            dir_vector = final_position - initial_position

            # Divide directional vector as a series of vector of norm 10um
            step_vector = 15 * dir_vector/np.linalg.norm(dir_vector)

            # Number of sub-directional vector to make
            nb_step = np.linalg.norm(dir_vector) / 15.

            # Moving the arm
            for step in range(1, int(nb_step)+1):
                intermediate_position = step * self.inv_mat * step_vector
                self.arm.absolute_move_group(self.inv_mat*initial_position + intermediate_position, [0, 1, 2])
                time.sleep(0.1)

            # make final move to desired position
            self.arm.absolute_move_group(self.inv_mat*final_position, [0, 1, 2])
        pass

    def pipettechange(self):

        """
        Change pipette & recalibration
        """

        # Get the direction to get the pipette out
        ratio = fabs(self.mat[0, 0] / self.mat[1, 0])

        if ratio > 1:
            i = 0
        else:
            i = 1

        if (self.template_loc[i] != 0) ^ (self.mat[i, 0] > 0):
            sign = 1
        else:
            sign = -1

        # Get the pipette out
        self.arm.relative_move(sign * 20000, 0)
        self.arm.wait_motor_stop(0)

        # Wait until the user change the pipette and press a key
        key = cv2.waitKey(0)
        if key & 0xFF == ord('q'):
            return 0, 0

        # Approching the pipette until on screen
        self.arm.relative_move(-sign * 17000, 0)
        self.arm.wait_motor_stop(0)

        while 1:
            self.arm.relative_move(100, 0)
            self.arm.wait_motor_stop(0)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                return 0
            img = self.template_zone()

            isin, val, loc = templatematching(img, self.template[len(self.template) / 2])

            if isin:
                while 0.98 > val:
                    val, _, loc = self.focus()

                delta = np.array([[(self.x_init - loc[0]) * self.um_px], [(self.y_init - loc[1]) * self.um_px]])
                move = self.rot_inv * delta
                for i in range(2):
                    self.arm.relative_move(move[i, 0], i)
                self.arm.wait_motor_stop([0, 1])
                # Change zero position to current position
                self.arm.set_to_zero([0, 1, 2])
                self.microscope.set_to_zero([0, 1, 2])
                break
        pass

    def get_image_series(self, nb_img=51):
        z_pos = self.microscope.position(2)
        for k in range(nb_img):
            self.microscope.absolute_move(z_pos + k - (nb_img - 1) / 2, 2)
            self.microscope.wait_motor_stop(2)
            time.sleep(1)
            img = self.cam.frame
            cv2.imwrite('./screenshots/series{}.jpg'.format(k), img)
        self.microscope.absolute_move(z_pos, 2)

    def get_template_series(self, nb_images):
        """
        Get a series of template images of the tip, at different height, around the center of an image.
        :param nb_images: number of template images to take, must be odd
        """

        # Tab for the series of images
        self.template = []

        # Tab
        temp = []

        # Make current position the zero position
        self.arm.set_to_zero([0, 1, 2])
        self.microscope.set_to_zero([0, 1, 2])

        # Take imges only in the template zone
        template = self.template_zone()
        height, width = template.shape[:2]

        # Tab of weight to detect where the pipette is
        weight = []

        # Detecting the tip
        for i in range(3):
            for j in range(3):
                if (i != 1) & (j != 1):
                    # divide template zone into 9 images
                    temp = template[i * height / 4:height / 2 + i * height / 4, j * width / 4:width / 2 + j * width / 4]

                    # Search the tip using the number of darkest pixel in the image
                    bin_edge, _ = np.histogram(temp.flatten())
                    weight += [bin_edge.min()]
                else:
                    # image is the center of template zone, do not consider to have functional get_withdraw_sign method
                    weight += [-1]

        # pipette is in the image with the most darkest pixels
        index = weight.index(max(weight))
        j = index % 3
        i = index // 3

        # Update the position of the tip in image
        self.template_loc = [temp.shape[1] * (1 - j / 2.), temp.shape[0] * (1 - i / 2.)]

        # Get the series of template images at different height
        for k in range(nb_images):
            self.microscope.absolute_move(k - (nb_images - 1) / 2, 2)
            self.microscope.wait_motor_stop(2)
            time.sleep(1)
            img = self.template_zone()
            height, width = img.shape[:2]
            img = img[i * height / 4:height / 2 + i * height / 4, j * width / 4:width / 2 + j * width / 4]
            self.template += [img]

        # reset position at the end
        self.go_to_zero()
        pass

    def focus(self):
        """
        Autofocus by searching the best template match in the image.
        :return maxval: percentage rate of how close the current image is to one of the template image
        :return dep: displacement made to focus
        :return loc: tab location of the detected template image
        """

        # Getting the microscope height
        current_z = self.microscope.position(2)

        # Tabs of maximum match value and their location during the process
        vals = []
        locs = []

        # Getting the maxvals and their locations
        for i in self.template:

            res, val, loc = templatematching(self.cam.frame, i)
            locs += [loc]

            if res:
                # Template has been detected
                vals += [val]
            else:
                # Template has not been detected, val set at 0
                vals += [0]

        # Search of the highest value, indicating which template image match the best the current image
        maxval = max(vals)

        if maxval != 0:
            # At least one template has been detected, setting the microscope at corresponding height
            index = vals.index(maxval)
            loc = locs[index]
            focus_height = current_z + len(self.template) // 2 - index
            self.microscope.absolute_move(focus_height, 2)
            self.microscope.wait_motor_stop(2)
            dep = len(self.template) // 2 - index
        else:
            # No template has been detected, focus can not be achieved
            raise ValueError('The template image has not been detected.')

        return maxval, dep, loc

    def focus_track(self, step, axis):
        """
        Focus after a move of the arm
        """

        # Move the arm
        self.arm.relative_move(step, axis)

        # Move the platform to center the tip
        for i in range(3):
            self.microscope.relative_move(self.mat[i, axis] * step, i)

        # Waiting for motors to stop
        self.arm.wait_motor_stop(axis)
        self.microscope.wait_motor_stop([0, 1, 2])

        # Focus around the estimated focus height
        try:
            _, _, loc = self.focus()
        except ValueError:
            raise EnvironmentError('Could not focus on the tip')

        # Move the platform for compensation
        delta = np.array([[(self.x_init - loc[0]) * self.um_px], [(self.y_init - loc[1]) * self.um_px], [0]])
        move = self.rot_inv * delta
        for i in range(2):
            self.microscope.relative_move(move[i, 0], i)

        self.microscope.wait_motor_stop([0, 1])

        # Update the estimated move to do for a move of 1 um of the arm
        for i in range(3):
            self.mat[i, axis] = self.microscope.position(i)/self.arm.position(axis)

        pass

    def matrix_accuracy(self):
        """
        Compute the accuracy of the transform matrix
        """
        acc = [0, 0, 0]
        for i in range(3):
            temp = 0
            for j in range(3):
                temp += self.mat[j, i]**2
            acc[i] = temp**0.5
        return acc

    def template_zone(self):
        """
        Gives the image at the center of the camera frame
        :return: 
        """
        ratio = 32
        shape = [self.cam.height, self.cam.width]
        img = self.cam.frame[shape[0] / 2 - 3 * shape[0] / ratio:shape[0] / 2 + 3 * shape[0] / ratio,
                             shape[1] / 2 - 3 * shape[1] / ratio:shape[1] / 2 + 3 * shape[1] / ratio]
        return img

    def save_img(self):
        """
        Save a screenshot
        :return:
        """
        self.cam.save_img()
        self.update_message('Screenshot saved.')
        pass

    def set_continuous_meter(self, enable):
        """
        Enable/disable continuous resistance metering
        :param enable: Bool for (de)activation
        :return: 
        """
        if enable:
            self.amplifier.start_continuous_acquisition()
        else:
            self.amplifier.stop_continuous_acquisition()

    def get_single_resistance_metering(self, res_type='float'):
        """
        Get a single resistance meter
        :param res_type: type of return. Either float or text
        :return: 
        """
        self.amplifier.get_discrete_acquisition()
        return self.get_resistance(res_type=res_type)

    def get_resistance(self, res_type='float'):
        """
        Get the resistance metered by the amplifier
        :param res_type: type of return. Either text or float
        :return: 
        """
        if res_type == 'text':
            # Output to be a string
            # Transform value (in Ohm) as a int string
            val = str(int(self.amplifier.res))

            # Compute displayable unit of the value
            unit = (len(val) - 1) // 3
            length = len(val) - unit * 3
            if unit <= 0:
                unit = ' Ohm'
            elif unit == 1:
                unit = ' kOhm'
            elif unit == 2:
                unit = ' MOhm'
            elif unit == 3:
                unit = ' GOhm'
            elif unit == 4:
                unit = ' TOhm'
            else:
                unit = ' 1E{} Ohm'.format(unit * 3)

            # Change the unit of the value
            if len(val) < length + 3:
                text_value = val[:length] + '.' + val[length:] + unit
            else:
                text_value = val[:length] + '.' + val[length:length + 2] + unit

            return text_value

        elif res_type == 'float':
            # Output to be a float
            return self.amplifier.res

    def get_potential(self, res_type='float'):
        """
        Get the potential measured by the amplifier
        :param res_type: type of return. Either text or float
        :return: 
        """
        if res_type == 'text':
            # Output to be a string
            # Transform value (in Ohm) as a int string
            val = self.amplifier.pot
            sign = val/abs(val)
            val = str(int(abs(val*1e3)))

            # Compute displayable unit of the value
            unit = (len(val) - 1) // 3
            length = len(val) - unit * 3
            if unit <= 0:
                unit = ' mV'
            elif unit == 1:
                unit = ' V'
            elif unit == 2:
                unit = ' kV'
            elif unit == 3:
                unit = ' MV'
            elif unit == 4:
                unit = ' GV'
            else:
                unit = ' 1E{} V'.format((unit-1) * 3)

            # Change the unit of the value
            if len(val) < length + 3:
                text_value = '-'*(sign < 0) + val[:length] + '.' + val[length:] + unit
            else:
                text_value = '-'*(sign < 0) + val[:length] + '.' + val[length:length + 2] + unit

            return text_value

        elif res_type == 'float':
            # Output to be a float
            return self.amplifier.pot

    def init_patch_clamp(self):
        """
        Check conditions for patch (pipette resistance)
        :return: 
        """

        self.pressure.nearing()

        # Auto pipette offset and holding at 0 V
        self.amplifier.meter_resist_enable(False)
        self.amplifier.auto_pipette_offset()
        self.amplifier.set_holding(0.)
        self.amplifier.set_holding_enable(True)

        # Begin metering
        self.amplifier.meter_resist_enable(True)
        # wait for stable measure
        time.sleep(4)
        # Get pipette resistance
        self.pipette_resistance = self.get_single_resistance_metering(res_type='float')
        if 5e6 > self.pipette_resistance:
            self.update_message('ERROR: Tip resistance is too low ({}).'
                                ' Should be higher than 5 MOhm.'.format(self.get_single_resistance_metering('text')))
            self.amplifier.meter_resist_enable(False)
            return 0
        if 10e6 < self.pipette_resistance:
            self.update_message('ERROR: Tip resistance is too high ({}).'
                                ' Should be lower than 10 MOhm.'.format(self.get_single_resistance_metering('text')))
            self.amplifier.meter_resist_enable(False)
            return 0
        else:
            self.update_message('Tip resistance is good: {}'.format(self.get_single_resistance_metering('text')))
            self.pipette_resistance_checked = True
            self.set_continuous_meter(True)
            return 1

    def patch(self, position):
        """
        Make a patch at given position
        :param position: absolute position (microscope referential) to make the patch
        :return: 
        """
        # Get the corresponding position in the pipette referential
        tip_position = self.inv_mat * position

        # Approaching cell 1um by 1um
        self.update_message('Approaching cell...')
        while self.withdraw_sign * (self.arm.position(0) - tip_position[0, 0]) + 3 > 0:
            # Arm is not beyond the desired position, moving
            self.arm.step_move(-self.withdraw_sign, 0)
            self.arm.wait_motor_stop([0])
            time.sleep(1)
            if self.pipette_resistance * 1.15 < self.get_resistance():
                # pipette resistance has increased: probably close to cell, wait for stablilization
                time.sleep(10)
                if self.pipette_resistance * 1.15 < self.get_resistance():
                    # Resistance has not decreased, stop moving
                    # Close to the cell, sealing
                    self.update_message('Cell found. Sealing...')
                    self.pressure.seal()
                    init_time = time.time()
                    self.amplifier.set_holding_enable(True)
                    while (1e9 > self.get_resistance()) | (time.time() - init_time < 15):
                        # Waiting for measure to increased to 1GOhm
                        if time.time() - init_time < 10:
                            # decrease holding to -70mV in 10 seconds
                            self.amplifier.set_holding(-7 * 1e-3 * (time.time() - init_time))
                            self.amplifier.set_holding_enable(True)
                        if time.time() - init_time >= 90:
                            # Resistance did not increased enough in 90sec: failure
                            self.update_message('ERROR: Seal unsuccessful.')
                            return 0
                    # Seal succesfull
                    self.pressure.release()
                    self.update_message('Patch done.')
                    return 1

        # Broke the loop because arm went too far without finding the cell
        self.update_message('ERROR: Could not find the cell.')
        return 0

    def clamp(self):
        """
        Clamping in actual position
        :return: 
        """
        nb_try = 0
        if 1e9 > self.get_resistance('float'):
            self.update_message('ERROR: Seal has not been accomplished.')
            return 0
        self.update_message('Clamping...')
        self.amplifier.meter_resist_enable(True)
        while 300e6 < self.get_resistance():
            # Breaking in while resistance does not correspond to interior of cell
            self.amplifier.zap()
            self.pressure.break_in()
            time.sleep(1.3)
            nb_try += 1
            if nb_try == 4:
                # Too many tries: failure
                self.update_message('ERROR: Clamp unsuccessful.')
                return 0
        # Broke in the cell
        self.amplifier.meter_resist_enable(False)
        time.sleep(.5)
        self.amplifier.null_current()
        self.update_message('Clamp done.')
        return 1

    def update_message(self, text):
        """
        Update messages and display them if verbose is True
        :param text: text's message 
        :return: 
        """
        self.message = text
        if self.verbose:
            print self.message

    def save_position(self):
        pass

    def stop(self):
        """
        Stop all threads linked to the robot
        :return: 
        """
        self.running = False
        self.cam.stop()
        self.amplifier.stop()
        pass

if __name__ == '__main__':
    robot = PatchClampRobot('SM5', 'dev1', 'Hamamatsu')
    calibrated = 0
    while 1:

        key = cv2.waitKey(1)

        if key & 0xFF == ord('q'):
            break

        if key & 0xFF == ord('t'):
            if robot.template:
                for i in robot.template:
                    _, val, _ = templatematching(robot.cam.frame, i)
                    print val

        if key & 0xFF == ord('z'):
            robot.go_to_zero()

        if key & 0xFF == ord('b'):
            calibrated = robot.calibrate()
            if not calibrated:
                print 'Calibration canceled.'
        if calibrated:
            robot.enable_click_position()

    del robot
