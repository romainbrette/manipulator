from threading import Thread
from camera_init import *
from img_functions import *
import numpy as np
import cv2
import os
import errno

__all__ = ['Camera']


class Camera(Thread):
    """
    Camera thread to refresh screen while making moves
    """

    def __init__(self, camera_name, mouse_fun, img_func=None, winname='Camera'):

        # init thread
        Thread.__init__(self)

        # init camera device
        self.camera_name = camera_name
        self.cam, self.flip = camera_init(camera_name)

        # Initializing variables for display
        self.frame = None
        self.img_to_display = None
        self.width, self.height = self.cam.getImageWidth(), self.cam.getImageHeight()
        self.winname = winname
        self.show = True
        self.click_on_window = False

        # OnMouse function when clicking on the window
        self.mouse_callback = mouse_fun
        self.img_fun = img_func
        self.start()

    def run(self):
        """
        Thread run, display camera frames
        :return: 
        """
        # start image acquisition
        self.cam.startContinuousSequenceAcquisition(1)
        # name the window
        cv2.namedWindow(self.winname, flags=cv2.WINDOW_NORMAL)

        while self.show:
            if self.cam.getRemainingImageCount() > 0:
                # New image has been taken by the camera
                temp_frame = self.cam.getLastImage()
                temp_frame = cv2.cvtColor(temp_frame, cv2.COLOR_GRAY2BGR)

                # Convert to 8 bit gray scale
                if temp_frame.dtype == 'uint8':
                    img = cv2.convertScaleAbs(temp_frame)
                elif temp_frame.dtype == 'uint16':
                    img = cv2.convertScaleAbs(temp_frame, alpha=2**-2)
                else:
                    img = cv2.convertScaleAbs(temp_frame)

                if self.flip[0]:
                    # image has to be flipped
                    img = cv2.flip(img, self.flip[1])

                # Update attributes
                self.frame = img

                # Display the image with a cross at the center
                img_to_display = disp_centered_cross(img)
                if self.img_fun is not None:
                    self.img_fun(img_to_display)
                cv2.imshow(self.winname, img_to_display)
                cv2.waitKey(1)

                if self.click_on_window:
                    # Clicking on window enabled
                    cv2.setMouseCallback(self.winname, self.mouse_callback)

        # End of Thread, stop acquisition and destroy
        self.cam.stopSequenceAcquisition()
        camera_unload(self.cam)
        self.cam.reset()
        cv2.destroyAllWindows()

    def save_img(self):
        """
        Save a screenshot
        :return: 
        """
        path = './screenshots/'
        # Check if path exist, creates it if not
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as exc:
                # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        # Translate the image as a 8bit image
        img = self.frame
        n_img = len(os.listdir(path))+1
        cv2.imwrite('./screenshots/screenshot{n}.jpg'.format(n=n_img), img)
        pass

    def switch_mouse_callback(self):
        """
        Enable/disable mouse callback on window
        :return: 
        """
        self.mouse_callback ^= 1

    def stop(self):
        self.show = False
