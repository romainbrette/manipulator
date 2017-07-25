from threading import Thread
from camera_init import *
from img_functions import *
import cv2
import os
import errno
import numpy as np

__all__ = ['CameraThread']


class CameraThread(Thread):
    """
    Camera thread to refresh screen while making moves
    """

    def __init__(self, camera_name, mouse_fun, winname='Camera'):

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
        self.recording = False

        # OnMouse function when clicking on the window
        self.mouse_callback = mouse_fun
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

        path = './video/'
        # Check if path exist, if not, creates it.
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as exc:
                # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        video = cv2.VideoWriter('./video/Capture.avi',
                                -1,
                                9.,
                                (self.width, self.height),
                                False)

        while self.show:
            if self.cam.getRemainingImageCount() > 0:
                # New image has been taken by the camera
                temp_frame = self.cam.getLastImage()

                # Convert to 8 bit gray scale
                img = cv2.convertScaleAbs(temp_frame)

                # Increase contrast (Contrast Limited Adaptive Histogram Equalization)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                img = clahe.apply(img)

                if self.flip[0]:
                    # image has to be flipped
                    img = cv2.flip(img, self.flip[1])

                # Update attributes
                self.frame = img
                if self.recording:
                    video.write(img)

                # Display the image with a cross at the center
                img_to_display = disp_centered_cross(img)
                cv2.imshow(self.winname, img_to_display)
                cv2.waitKey(1)

                if self.click_on_window:
                    # Clicking on window enabled
                    cv2.setMouseCallback(self.winname, self.mouse_callback)

        # End of Thread, stop acquisition and destroy
        video.release()
        self.cam.stopSequenceAcquisition()
        camera_unload(self.cam)
        self.cam.reset()
        cv2.destroyAllWindows()

    def save_img(self):
        """
        Save a screenshot
        :return: 
        """
        path = './{i}/screenshots/'.format(i=self.camera_name)
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
        cv2.imwrite('./{i}/screenshots/screenshot{n}.jpg'.format(i=self.camera_name, n=n_img), img)
        pass

    def switch_mouse_callback(self):
        """
        Enable/disable mouse callback on window
        :return: 
        """
        self.mouse_callback ^= 1

    def stop(self):
        self.show = False
