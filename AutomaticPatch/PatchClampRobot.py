from Autofocus import *
from Camera import *
from Amplifier import *
from Pump import *
import numpy as np
import cv2
from math import fabs
from time import sleep, time
import os
import errno
import time

__all__ = ['PatchClampRobot']


class PatchClampRobot(object):

    def __init__(self, controller, arm):

        # devices
        self.dev, self.microscope, self.arm = init_device(controller, arm)
        self.controller = controller

        # Tab for template images
        self.template = []

        # Boolean for calibrated state
        self.calibrated = 0

        # Maximum distance from initial position allowed
        self.maxdist = 2000

        # Initial displacement of the arm to do during autocalibration, in um
        self.first_step = 2.
        self.step = 0

        # Rotation matrix of the platform compared to the camera
        self.rot = np.matrix([[0., 0.], [0., 0.]])
        self.rot_inv = np.matrix([[0., 0.], [0., 0.]])

        # Initializing transformation matrix (Jacobian) between the camera and the tip
        self.mat = np.matrix([[0., 0., 0.], [0., 0., 0.], [0., 0., 0.]])
        self.inv_mat = np.matrix([[0., 0., 0.], [0., 0., 0.], [0., 0., 0.]])

        # Initial position of the tip in the image, before calibration
        self.x_init, self.y_init = 0, 0

        # Ratio um/pixel of the camera
        self.um_px = 0.

        # Position of the tip in the template image
        self.template_loc = [0., 0.]

        # Withdraw direction - changed at end of calibration
        self.withdraw_sign = 1

        # Resistance data
        self.pipette_resistance = 0.
        self.pipette_resistance_checked = False

        # Camera
        self.amplifier = ResistanceMeter('Multiclamp')
        self.pressure = PressureController('OB1')
        self.cam = CameraThread(controller, self.clic_position)
        pass

    def go_to_zero(self):
        """
        Make the arm and platform go to the origin: state before the calibration
        """

        self.arm.go_to_zero([0, 1, 2])
        self.microscope.go_to_zero([0, 1, 2])
        self.arm.wait_motor_stop([0, 1, 2])
        self.microscope.wait_motor_stop([0, 1, 2])
        sleep(.2)
        pass

    def calibrate_platform(self):
        """
        Calibrate the platform:
        Reset zero position to current position
        Compute rotation matrix between the platform and camera 
        """

        # Make current position the zero position
        self.arm.set_to_zero([0, 1, 2])
        self.microscope.set_to_zero([0, 1, 2])

        # Testing if difference exits between first and second counter
        self.arm.set_to_zero_second_counter([0, 1, 2])
        self.microscope.set_to_zero_second_counter([0, 1, 2])

        # Get a series of template images for auto focus
        self.get_template_series(5)

        # Saving initial position of the tip on the screen
        _, _, loc = templatematching(self.cam.frame, self.template[len(self.template) // 2])
        self.x_init, self.y_init = loc[:2]

        # Getting the rotation matrix between the platform and the camera
        for i in range(2):

            # Moving the microscope
            self.microscope.relative_move(120, i)
            self.microscope.wait_motor_stop(i)
            sleep(.5)

            # Getting the displacement, in pixels, of the tip on the screen
            _, _, loc = templatematching(self.cam.frame, self.template[len(self.template) // 2])
            dx = loc[0] - self.x_init
            dy = loc[1] - self.y_init

            # Determination of um_px
            dist = (dx ** 2 + dy ** 2) ** 0.5
            self.um_px = self.microscope.position(i) / dist

            # Compute the rotation matrix
            self.rot[0, i] = dx / dist
            self.rot[1, i] = dy / dist

            # Resetting position of microscope
            self.microscope.go_to_zero([i])

        # Inverse rotation matrix for future use
        self.rot_inv = np.linalg.inv(self.rot)
        pass

    def calibrate_arm(self, axis):
        """
        Calibrate the arm along axis.
        :param axis: axis to calibrate
        :return: 0 if calibration failed, 1 otherwise
        """

        while self.arm.position(axis) < self.maxdist:

            # calibrate arm axis using exponential moves:
            # moves the arm, recenter the tip and refocus.
            # displacements are saved
            try:
                self.exp_focus_track(axis)
            except EnvironmentError:
                print 'Could not track the tip.'
                return 0

        # When calibration is finished:

        # Resetting position of arm and microscope so no error gets to the next axis calibration
        self.go_to_zero()
        sleep(2)

        return 1

    def get_withdraw_sign(self):
        if fabs(self.mat[0, 0] / self.mat[1, 0]) > 1:
            i = 0
        else:
            i = 1
        if (self.template_loc[i] != 0) ^ (self.mat[i, 0] > 0):
            self.withdraw_sign = 1
        else:
            self.withdraw_sign = -1
        pass

    def calibrate(self):
        """
        Calibrate the entire Robot
        :return: 0 if calibration failed, 1 otherwise
        """

        print 'Calibrating platform'

        self.calibrate_platform()

        print 'Platform Calibrated'

        # calibrate arm x axis
        print 'Calibrating x axis'
        calibrated = self.calibrate_arm(0)

        if not calibrated:
            return 0
        else:
            print 'x axis calibrated'

        # calibrate arm y axis
        print 'Calibrating y axis'
        calibrated = self.calibrate_arm(1)

        if not calibrated:
            return 0
        else:
            print 'y axis calibrated'

        # calibrate arm z axis
        print 'Calibrating z axis'
        calibrated = self.calibrate_arm(2)

        if not calibrated:
            return 0
        else:
            print 'z axis calibrated'

        # Getting the direction to withdraw pipette along x axis
        self.get_withdraw_sign()
        self.inv_mat = np.linalg.inv(self.mat)
        self.calibrated = 1
        self.cam.clic_on_window = True
        self.save_calibration()
        return 1

    def save_calibration(self):

        path = './{}/'.format(self.controller)
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as exc:
                # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open("./{i}/mat.txt".format(i=self.controller), 'wt') as f:
            for i in range(3):
                f.write('{a},{b},{c}\n'.format(a=self.mat[i, 0], b=self.mat[i, 1], c=self.mat[i, 2]))

        with open("./{i}/rotmat.txt".format(i=self.controller), 'wt') as f:
            for i in range(2):
                f.write('{a},{b}\n'.format(a=self.rot[i, 0], b=self.rot[i, 1]))

        with open('./{i}/data.txt'.format(i=self.controller), 'wt') as f:
            f.write('{d}\n'.format(d=self.um_px))
            f.write('{d}\n'.format(d=self.x_init))
            f.write('{d}\n'.format(d=self.y_init))
            f.write('{d}\n'.format(d=self.template_loc[0]))
            f.write('{d}\n'.format(d=self.template_loc[1]))

    def load_calibration(self):
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
                    for j in range(2):
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
            self.cam.clic_on_window = True
            return 1

        except IOError:
            print '{i} has not been calibrated.'.format(i=self.controller)
            return 0

    def clic_position(self, event, x, y, flags, param):
        """
        Position the tip where the user has clic on the window image.
        Shall be used along cv2.setMouseCallback
        :param event: Type of mouse interaction with the window (auto) 
        :param x: position x of the event (auto)
        :param y: position y of the event (auto)
        :param flags: extra flags (auto)
        :param param: extra parameters (auto)
        :return: 
        """
        if self.calibrated:
            if event == cv2.EVENT_LBUTTONUP:
                #pos = np.array([[0], [0], [0]])
                #for i in range(3):
                #    pos[i, 0] = self.microscope.position(i)

                pos = np.transpose(self.microscope.position())

                temp = self.rot_inv * np.array([[(self.x_init - (x - self.template_loc[0])) * self.um_px],
                                                [(self.y_init - (y - self.template_loc[1])) * self.um_px]])
                pos[0, 0] += temp[0, 0]
                pos[1, 0] += temp[1, 0]

                self.linear_move(self.mat*np.transpose(self.arm.position()), pos)
                #move = self.inv_mat * pos

                #self.arm.absolute_move_group(move, [0, 1, 2])

            elif event == cv2.EVENT_RBUTTONUP:

                if self.pipette_resistance_checked | (not self.pipette_resistance_checked):

                    mic_pos = np.transpose(self.microscope.position())

                    temp = self.rot_inv * np.array([[(self.x_init - (x - self.template_loc[0])) * self.um_px],
                                                    [(self.y_init - (y - self.template_loc[1])) * self.um_px]])
                    mic_pos[0, 0] += temp[0, 0]
                    mic_pos[1, 0] += temp[1, 0]

                    final_tip_pos = self.inv_mat*mic_pos
                    tip_pos = self.mat*np.transpose(self.arm.position())

                    if tip_pos[2, 0] < mic_pos[2, 0]:
                        move = self.withdraw_sign*(mic_pos[2, 0]-tip_pos[2, 0]+15)/abs(self.mat[2, 0])
                        self.arm.relative_move(0, move)
                        theorical_tip_pos = tip_pos + np.array([[move], [0], [0]])
                    else:
                        self.arm.relative_move(self.withdraw_sign*15/abs(self.mat[2, 0]), 0)
                        theorical_tip_pos = tip_pos + np.array([[self.withdraw_sign*15/abs(self.mat[2, 0])], [0], [0]])

                    self.arm.wait_motor_stop([0])
                    intermediate_x_tip_pos = self.withdraw_sign*(theorical_tip_pos[2, 0]-mic_pos[2, 0])/abs(self.mat[2, 0])
                    intermediate_pos = mic_pos
                    intermediate_pos += self.mat*np.array([[intermediate_x_tip_pos], [0], [0]])
                    self.linear_move(theorical_tip_pos, intermediate_pos)
                    self.arm.wait_motor_stop([0, 1, 2])
                    self.linear_move(intermediate_pos, mic_pos)
                    #self.linear_move(intermediate_pos, mic_pos+self.mat*np.array([[self.withdraw_sign*10], [0], [0]]))

                    if abs(self.pipette_resistance-self.get_resistance()) > 3e5:
                        raise ValueError
                    else:
                        self.amplifier.auto_pipette_offset()
                        while self.arm.position(0)-final_tip_pos[0, 0]-self.withdraw_sign*5 > 0:
                            self.arm.relative_move(-self.withdraw_sign)
                            if self.pipette_resistance*1.25 < self.get_resistance():
                                break
                        sleep(10)
                        if self.pipette_resistance*1.25 < self.get_resistance():
                            self.pressure.seal()

        pass

    def enable_clic_position(self):
        cv2.setMouseCallback(self.cam.winname, self.clic_position)
        pass

    def linear_move(self, initial_position, final_position):
        """
        Goes to an absolute position in straight line.
        The initial position can be hypothetical (to auto correct motors limit) or true current position
        :param initial_position: absolute position to begin the movement with. (ndarray)
        :param final_position: absolute position to go. (ndarray)
        :return: none
        """
        
        dir_vector = final_position - initial_position
        step_vector = 10. * dir_vector/np.linalg.norm(dir_vector)
        nb_step = np.linalg.norm(dir_vector) / 10.
        for step in range(1, int(nb_step)+1):
            intermediate_position = step * self.inv_mat * np.transpose(step_vector)
            self.arm.absolute_move_group(initial_position + intermediate_position, [0, 1, 2])
        self.arm.absolute_move_group(self.inv_mat*np.transpose(final_position), [0, 1, 2])

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

    def get_template_series(self, nb_images):
        """
        Get a series of template images of the tip around the center of an image for any angle of the tip.
        :param nb_images: number of template images to take, must be odd
        """
        self.template = []
        temp = []

        template = self.template_zone()
        height, width = template.shape[:2]
        weight = []
        for i in range(3):
            for j in range(3):
                if (i != 1) & (j != 1):
                    temp = template[i * height / 4:height / 2 + i * height / 4, j * width / 4:width / 2 + j * width / 4]
                    bin_edge, _ = np.histogram(temp.flatten())
                    weight += [bin_edge.min()]

        index = weight.index(max(weight))
        j = index % 3
        i = index // 3
        self.template_loc = [temp.shape[1] * (1 - j / 2.), temp.shape[0] * (1 - i / 2.)]

        for k in range(nb_images):
            self.microscope.absolute_move(k - (nb_images - 1) / 2, 2)
            self.microscope.wait_motor_stop(2)
            time.sleep(0.5)
            img = self.template_zone()
            height, width = img.shape[:2]
            img = img[i * height / 4:height / 2 + i * height / 4, j * width / 4:width / 2 + j * width / 4]
            self.template += [img]
        self.go_to_zero()
        pass

    def focus(self):
        """
        Autofocus by searching the best template match in the image.
        :return maxval: percentage rate of how close the current image is to one of the template image
        :return dep: displacement made to focus
        :return loc: tab location of the detected template image
        """

        # Getting the microscope height according to the used controller
        current_z = self.microscope.position(2)

        # Tabs of maxval and their location during the process
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

    def exp_focus_track(self, axis):
        """
        Focus after a move of the arm along axis
        """

        if self.arm.position(axis) == 0:
            self.step = self.first_step
        else:
            self.step *= 2.

        # Move the arm
        self.arm.step_move(axis, self.step)

        # Move the platform to center the tip
        for i in range(3):
            self.microscope.step_move(i, self.mat[i, axis] * self.step)

        # Waiting for motors to stop
        self.arm.wait_motor_stop(axis)
        self.microscope.wait_motor_stop([0, 1, 2])

        # Focus around the estimated focus height
        try:
            _, _, loc = self.focus()
        except ValueError:
            raise EnvironmentError('Could not focus on the tip')

        # Move the platform for compensation
        delta = np.array([[(self.x_init - loc[0]) * self.um_px], [(self.y_init - loc[1]) * self.um_px]])
        move = self.rot_inv * delta
        for i in range(2):
            self.microscope.step_move(i, move[i, 0])

        self.microscope.wait_motor_stop([0, 1])

        # Update the estimated move to do for a move of 1 um of the arm
        for i in range(3):
            self.mat[i, axis] = self.microscope.position(i)/self.arm.position(axis)

        pass

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
        delta = np.array([[(self.x_init - loc[0]) * self.um_px], [(self.y_init - loc[1]) * self.um_px]])
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
        Compute the accuracy of the transformation matrix
        """
        acc = [0, 0, 0]
        for i in range(3):
            temp = 0
            for j in range(3):
                temp += self.mat[j, i]**2
            acc[i] = temp**0.5
        return acc

    def template_zone(self):
        ratio = 32
        shape = [self.cam.height, self.cam.width]
        img = self.cam.frame[shape[0] / 2 - 3 * shape[0] / ratio:shape[0] / 2 + 3 * shape[0] / ratio,
                             shape[1] / 2 - 3 * shape[1] / ratio:shape[1] / 2 + 3 * shape[1] / ratio]
        return img

    def save_img(self):
        self.cam.save_img()
        pass

    def set_continuous_res_meter(self, enable):
        if enable:
            self.amplifier.start_continuous_acquisition()
        else:
            self.amplifier.stop_continuous_acquisition()

    def get_one_res_metering(self, res_type='float'):
        self.amplifier.get_discrete_acquisition()
        return self.get_resistance(res_type=res_type)

    def get_resistance(self, res_type='float'):
        if res_type == 'text':
            val = str(self.amplifier.res).split('.')
            unit = (len(val[0]) - 1) // 3
            length = len(val[0]) - unit * 3
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

            if len(val[0]) < length + 3:
                text_value = val[0][:length] + '.' + val[0][length:] + unit
            else:
                text_value = val[0][:length] + '.' + val[0][length:length + 2] + unit
            return text_value
        elif res_type == 'float':
            return self.amplifier.res

    def init_patch_clamp(self):
        self.amplifier.meter_resist_enable(False)
        self.amplifier.auto_pipette_offset()
        self.amplifier.set_holding(0.)
        self.amplifier.set_holding_enable(True)
        self.amplifier.meter_resist_enable(True)
        sleep(3)
        self.pipette_resistance = self.get_one_res_metering(res_type='float')
        if 4.5e6 > self.pipette_resistance:
            self.amplifier.meter_resist_enable(False)
            return 2
        if 10.2e6 < self.pipette_resistance:
            self.amplifier.meter_resist_enable(False)
            return 1
        else:
            self.pipette_resistance_checked = True
            self.pressure.nearing()
            self.set_continuous_res_meter(True)
            return 0

    def stop(self):
        self.cam.stop()
        self.amplifier.stop()
        cv2.destroyAllWindows()
        pass

if __name__ == '__main__':
    robot = PatchClampRobot('SM5', 'dev1')
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
            robot.enable_clic_position()

    del robot
