from autofocus import init_device, templatematching
from autofocus.Hamamatsu_camera import *
from img_functions import *
from numpy import matrix
from numpy.linalg import inv
import numpy as np
from math import fabs


class PatchClampRobot:

    def __init__(self, controller, arm):

        # devices
        self.dev, self.microscope, self.arm, self.cam = init_device(controller, arm)

        # Camera
        self.win_name = 'Camera'
        cv2.namedWindow(self.win_name, flags=cv2.WINDOW_NORMAL)
        self.frame = 0
        self.width = 50
        self.height = 50

        # Tab for template images
        self.template = []

        # Boolean for calibrated state
        self.calibrated = 0

        # Maximum distance from initial position allowed
        self.maxdist = 600

        # Initial displacement of the arm to do during autocalibration, in um
        self.first_step = 2.

        # Rotation matrix of the platform compared to the camera
        self.rot = matrix('0. 0.; 0. 0.')
        self.rot_inv = matrix('0. 0.; 0. 0.')

        # Initializing transformation matrix (Jacobian) between the camera and the tip
        self.mat = matrix('0. 0. 0.; 0. 0. 0.; 0. 0. 0.')
        self.inv_mat = matrix('0. 0. 0.; 0. 0. 0.; 0. 0. 0.')

        # Initial position of the tip in the image, before calibration
        self.x_init, self.y_init = 0, 0

        # Ratio um/pixel of the camera
        self.um_px = 0.

        # Position of the tip in the template image
        self.template_loc = [0., 0.]
        pass

    def go_to_zero(self):
        for i in range(3):
            self.arm.absolute_move(0, i)
            self.microscope.absolute_move(0, i)

        self.arm.wait_motor_stop([0, 1, 2])
        self.microscope.wait_motor_stop([0, 1, 2])
        pass

    def calibrate_platform(self):

        self.show()

        # Make current position the zero position
        self.arm.set_to_zero([0, 1, 2])
        self.microscope.set_to_zero([0, 1, 2])

        # Get a series of template images for auto focus
        self.get_template_series(5)

        # Saving initial position of the tip on the screen
        _, _, loc = templatematching(self.frame, self.template[len(self.template) / 2])
        self.x_init, self.y_init = loc[:2]

        # Getting the ratio um per pixels and the rotation of the platform

        for i in range(2):
            # Moving the microscope
            self.microscope.relative_move(150, i)
            self.microscope.wait_motor_stop(i)

            # Refreshing the frame after the move
            self.show()

            # Getting the displacement, in pixels, of the tip on the screen
            _, _, loc = templatematching(self.frame, self.template[len(self.template) / 2])
            dx = loc[0] - self.x_init
            dy = loc[1] - self.y_init

            # Determination of um_px
            dist = (dx ** 2 + dy ** 2) ** 0.5
            self.um_px = 150. / dist

            self.rot[0, i] = dx / dist
            self.rot[1, i] = dy / dist

            # Resetting position of microscope
            self.microscope.relative_move(-150, i)
            self.microscope.wait_motor_stop(i)

            # Refreshing frame
            self.show()

        self.rot_inv = inv(self.rot)
        pass

    def calibrate_arm(self, axis):

        self.show()

        while self.arm.position(axis) < self.maxdist:

            self.show()
            key = cv2.waitKey(1)

            if key & 0xFF == ord('q'):
                return 0

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

        # Update the frame
        self.show()

        return 1

    def calibrate(self):

        self.calibrate_platform()

        print 'Calibrated platform'

        # calibrate arm y axis

        calibrated = self.calibrate_arm(0)

        if not calibrated:
            return 0
        else:
            print 'Calibrated x axis'

        # calibrate arm y axis
        calibrated = self.calibrate_arm(1)

        if not calibrated:
            return 0
        else:
            print 'Calibrated y axis'

        # calibrate arm z axis
        calibrated = self.calibrate_arm(2)

        if not calibrated:
            return 0
        else:
            print 'Calibrated z axis'

        print self.mat
        print self.matrix_accuracy()
        self.inv_mat = inv(self.mat)
        print self.inv_mat
        print 'Calibration finished'
        self.calibrated = 1
        return 1

    def pipettechange(self):

        """
        Change pipette & recalibration
        """
        ratio = fabs(self.mat[0, 0] / self.mat[1, 0])

        if ratio > 1:
            i = 0
        else:
            i = 1

        if (self.template_loc[i] != 0) ^ (self.mat[i, 0] > 0):
            sign = 1
        else:
            sign = -1

        self.arm.relative_move(sign * 20000, 0)
        self.arm.wait_motor_stop(0)
        self.show()
        key = cv2.waitKey(0)
        if key & 0xFF == ord('q'):
            return 0, 0
        self.arm.relative_move(-sign * 17000, 0)
        self.arm.wait_motor_stop(0)
        self.show()

        while 1:
            self.arm.relative_move(100, 0)
            self.arm.wait_motor_stop(0)
            self.get_img()
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                return 0
            ratio = 32
            img = self.frame[self.height / 2 - 3 * self.height / ratio:self.height / 2 + 3 * self.height / ratio,
                             self.width / 2 - 3 * self.width / ratio:self.width / 2 + 3 * self.width / ratio]

            isin, val, loc = templatematching(img, self.template[len(self.template) / 2])

            if isin:
                while val < 0.98:
                    val, _, loc = self.focus()
                    self.show()

                delta = matrix('{a}; {b}'.format(a=(self.x_init - loc[0]) * self.um_px,
                                                 b=(self.y_init - loc[1]) * self.um_px))
                move = self.rot_inv * delta
                for i in range(2):
                    self.arm.relative_move(move[i, 0], i)
                self.arm.wait_motor_stop([0, 1])
                self.show()
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

        self.get_img()
        ratio = 32

        template = self.frame[self.height / 2 - 3 * self.height / ratio:self.height / 2 + 3 * self.height / ratio,
                              self.width / 2 - 3 * self.width / ratio:self.width / 2 + 3 * self.width / ratio]
        height, width = template.shape[:2]
        weight = []
        template = cv2.bilateralFilter(template, 9, 75, 75)
        for i in range(3):
            for j in range(3):
                temp = template[i * height / 4:height / 2 + i * height / 4, j * width / 4:width / 2 + j * width / 4]
                bin_edge, _ = np.histogram(temp.flatten())
                weight += [bin_edge.min()]

        index = weight.index(max(weight))
        j = index % 3
        i = index // 3
        self.template_loc = [temp.shape[1] * (1 - j / 2.), temp.shape[0] * (1 - i / 2.)]

        pos = self.microscope.position(2)

        for k in range(nb_images):
            self.show(pos - (nb_images - 1) / 2 + k)
            img = self.frame[self.height / 2 - 3 * self.height / ratio:self.height / 2 + 3 * self.height / ratio,
                             self.width / 2 - 3 * self.width / ratio:self.width / 2 + 3 * self.width / ratio]
            height, width = img.shape[:2]
            img = img[i * height / 4:height / 2 + i * height / 4, j * width / 4:width / 2 + j * width / 4]
            self.template += [img]
        self.show(pos)
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

        self.get_img()
        # Tabs of maxval and their location during the process
        vals = []
        locs = []

        # Getting the maxvals and their locations
        for i in self.template:

            res, val, loc = templatematching(self.frame, i)
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
            focus_height = current_z + len(self.template) / 2 - index
            self.show(focus_height)
            dep = len(self.template) / 2 - index
        else:
            # No template has been detected, focus can not be achieved
            raise ValueError('The template image has not been detected.')

        return maxval, dep, loc

    def exp_focus_track(self, axis):
        """
        Focus after a move of the arm
        """

        # Update frame just in case
        self.get_img()

        if self.arm.position(axis) == 0:
            step = self.first_step
        else:
            step = 2.*self.arm.position(axis)

        # Move the arm
        self.arm.relative_move(step, axis)

        # Move the platform to center the tip
        for i in range(3):
            self.microscope.relative_move(self.mat[i, axis] * step, i)

        # Waiting for motors to stop
        self.arm.wait_motor_stop(axis)
        self.microscope.wait_motor_stop([0, 1, 2])

        # Update the frame.
        self.show()

        # Focus around the estimated focus height
        try:
            _, _, loc = self.focus()
        except ValueError:
            raise EnvironmentError('Could not focus on the tip')

        # Move the platform for compensation
        delta = matrix('{a}; {b}'.format(a=(self.x_init - loc[0]) * self.um_px, b=(self.y_init - loc[1]) * self.um_px))
        move = self.rot_inv * delta
        for i in range(2):
            self.microscope.relative_move(move[i, 0], i)

        self.microscope.wait_motor_stop([0, 1])

        # Update frame
        self.show()

        # Update the estimated move to do for a move of 1 um of the arm
        for i in range(3):
            self.mat[i, axis] = self.microscope.position(i)/self.arm.position(axis)

        pass

    def focus_track(self, step, axis):
        """
        Focus after a move of the arm
        """

        # Update frame just in case
        self.get_img()

        # Move the arm
        self.arm.relative_move(step, axis)

        # Move the platform to center the tip
        #delta = matrix('{a}; {b}'.format(a=estim[0] * step, b=estim[1] * step))
        #move = self.rot_inv * delta
        for i in range(3):
            self.microscope.relative_move(self.mat[i, axis] * step, i)

        # Waiting for motors to stop
        self.arm.wait_motor_stop(axis)
        self.microscope.wait_motor_stop([0, 1, 2])

        # Update the frame.
        self.show()

        # Focus around the estimated focus height
        try:
            _, _, loc = self.focus()
        except ValueError:
            raise EnvironmentError('Could not focus on the tip')

        # Move the platform for compensation
        delta = matrix('{a}; {b}'.format(a=(self.x_init - loc[0]) * self.um_px, b=(self.y_init - loc[1]) * self.um_px))
        move = self.rot_inv * delta
        for i in range(2):
            self.microscope.relative_move(move[i, 0], i)

        self.microscope.wait_motor_stop([0, 1])

        # Update frame
        self.show()

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

    def show(self, z=None):
        self.get_img(z)
        if isinstance(self.frame, np.ndarray):
            self.height, self.width = self.frame.shape[:2]
            frame = disp_centered_cross(self.frame)
            # if not self.template:
            #     frame = disp_template_zone(frame)

            cv2.imshow(self.win_name, frame)
            cv2.waitKey(1)
        pass

    def get_img(self, z=None):

        """
        get an image from the microscope at given height z
        :param z: desired absolute height of the microscope
        :return frame: image taken from camera
        """

        # Move the microscope if an height has been specify
        if z:
            self.microscope.absolute_move(z, 2)
            self.microscope.wait_motor_stop(2)

        # capture frame

        if self.cam.getRemainingImageCount() > 0:

            self.frame = self.cam.getLastImage()
            self.frame = np.float32(self.frame/(1.0*self.frame.max()))
            self.frame = cv2.flip(self.frame, 2)

    def clic_position(self, event, x, y, flags, param):
        """
        :param event: 
        :param x: 
        :param y: 
        :param flags: 
        :param param:
        :return: 
        """
        if self.calibrated:
            if event == cv2.EVENT_LBUTTONUP:
                pos = matrix('0.; 0.; 0.')
                for i in range(3):
                    pos[i, 0] = self.microscope.position(i)

                temp = self.rot_inv * matrix([[(self.x_init - x + self.template_loc[0]) * self.um_px],
                                              [(self.y_init - y + self.template_loc[1]) * self.um_px]])
                pos[0, 0] += temp[0, 0]
                pos[1, 0] += temp[1, 0]

                move = self.inv_mat * pos
                for i in [2, 1, 0]:
                    self.arm.absolute_move(move[i], i)

        pass

    def enable_clic_position(self):
        cv2.setMouseCallback(self.win_name, self.clic_position)
        pass

    def __del__(self):
        self.cam.stopSequenceAcquisition()
        camera_unload(self.cam)
        self.cam.reset()
        del self.microscope
        cv2.destroyAllWindows()
        del self.dev
        pass
