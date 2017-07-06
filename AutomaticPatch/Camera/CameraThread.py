from threading import Thread
from camera_init import *
from img_functions import *
import cv2
import os
import errno
import numpy as np

__all__ = ['CameraThread']


class CameraThread(Thread):

    def __init__(self, camera_name, mouse_fun, winname='Camera'):
        Thread.__init__(self)
        self.camera_name = camera_name
        self.cam, self.flip = camera_init(camera_name)
        self.frame = None
        self.img_to_display = None
        self.width, self.height = None, None
        self.winname = winname
        self.show = True
        self.click_on_window = False
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

                if self.flip[0]:
                    img = cv2.flip(img, self.flip[1])

                self.frame = img
                self.height, self.width = img.shape[:2]
                img_to_display = disp_centered_cross(img)
                cv2.imshow(self.winname, img_to_display)
                cv2.waitKey(1)
                if self.click_on_window:
                    cv2.setMouseCallback(self.winname, self.mouse_callback)

        self.cam.stopSequenceAcquisition()
        camera_unload(self.cam)
        self.cam.reset()
        cv2.destroyAllWindows()

    def save_img(self):
        path = './{i}/screenshots/'.format(i=self.camera_name)
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as exc:
                # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        img = self.frame*256
        n_img = len(os.listdir(path))+1
        cv2.imwrite('./{i}/screenshots/screenshot{n}.jpg'.format(i=self.camera_name, n=n_img), img)
        pass

    def switch_mouse_callback(self):
        self.mouse_callback ^= 1

    def stop(self):
        self.show = False
