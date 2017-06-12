from threading import Thread
from camera import *
from img_functions import *
import cv2
import numpy as np

__all__ = ['CameraThread']


class CameraThread(Thread):

    def __init__(self, controller, winname='Camera'):
        Thread.__init__(self)
        self.controller = controller
        self.cam = camera_init(controller)
        self.frame = None
        self.width, self.height = None, None
        self.winname = winname
        cv2.namedWindow(self.winname, flags=cv2.WINDOW_NORMAL)
        self.n_img = 1
        self.show = 1

    def run(self):
        while 1:
            if self.show:
                self.get_img()
            else:
                cv2.destroyAllWindows()
                self.show = 1
                break

    def reverse_img(self):
        # Reverse the frame depending on the type of machine used
        if self.controller == 'SM5':
            self.frame = cv2.flip(self.frame, 2)
        elif self.controller == 'SM10':
            self.frame = cv2.flip(self.frame, 0)

    def get_img(self):

        """
        get an image from the camera
        """
        # capture frame

        if self.cam.getRemainingImageCount() > 0:

            self.frame = self.cam.getLastImage()
            self.frame = np.float32(self.frame/(1.0*self.frame.max()))
            self.reverse_img()
            self.height, self.width = self.frame.shape[:2]
            frame = disp_centered_cross(self.frame)

            cv2.imshow(self.winname, frame)
            cv2.waitKey(1)

    def save_img(self):
        cv2.imwrite('./{i}/screenshots/screenshot{n}'.format(i=self.controller, n=self.n_img), self.frame)
        self.n_img += 1
        pass

    def stop(self):
        self.show = 0
