from threading import Thread, Lock
from camera_init import *
from img_functions import *
import cv2
import os
import errno
import numpy as np

__all__ = ['CameraThread']

locked = Lock()


class CameraThread(Thread):

    def __init__(self, controller, mouse_fun, winname='Camera'):
        Thread.__init__(self)
        self.controller = controller
        self.cam = camera_init(controller)
        self.frame = None
        self.img_to_display = None
        self.width, self.height = None, None
        self.winname = winname
        self.show = True
        self.clic_on_window = False
        self.mouse_callback = mouse_fun
        self.start()

    def run(self):
        self.cam.startContinuousSequenceAcquisition(1)
        cv2.namedWindow(self.winname, flags=cv2.WINDOW_NORMAL)
        while self.show:
            if self.cam.getRemainingImageCount() > 0:
                temp_frame = self.cam.getLastImage()
                img = np.float32(temp_frame / (1. * temp_frame.max()))
                img **= 2
                img = cv2.bilateralFilter(img, 1, 10, 10)

                if self.controller == 'SM5':
                    img = cv2.flip(img, 2)
                elif self.controller == 'SM10':
                    img = cv2.flip(img, 1)

                self.frame = img
                self.height, self.width = img.shape[:2]
                img_to_display = disp_centered_cross(img)
                cv2.imshow(self.winname, img_to_display)
                cv2.waitKey(1)
                if self.clic_on_window:
                    cv2.setMouseCallback(self.winname, self.mouse_callback)

        self.cam.stopSequenceAcquisition()
        camera_unload(self.cam)
        self.cam.reset()

    def save_img(self):
        path = './{i}/screenshots/'.format(i=self.controller)
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as exc:
                # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        img = self.frame*256
        n_img = len(os.listdir(path))+1
        cv2.imwrite('./{i}/screenshots/screenshot{n}.jpg'.format(i=self.controller, n=n_img), img)
        pass

    def switch_mouse_callback(self):
        self.mouse_callback ^= 1

    def stop(self):
        self.show = False
