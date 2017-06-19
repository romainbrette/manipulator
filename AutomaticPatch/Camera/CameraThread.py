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
        self.width, self.height = None, None
        self.winname = winname
        cv2.namedWindow(self.winname, flags=cv2.WINDOW_NORMAL)
        self.n_img = 1
        self.show = True
        self.clic_on_window = False
        self.mouse_callback = mouse_fun

    def run(self):
        self.cam.startContinuousSequenceAcquisition(1)
        while self.show:
            with locked:
                if self.cam.getRemainingImageCount() > 0:
                    temp_frame = self.cam.getLastImage()
                    frame = np.float32(temp_frame / (1. * temp_frame.max()))

                    if self.controller == 'SM5':
                        frame = cv2.flip(frame, 2)
                    elif self.controller == 'SM10':
                        frame = cv2.flip(frame, 1)

                    self.frame = frame
                    self.height, self.width = frame.shape[:2]
                    frame = disp_centered_cross(frame)
                    cv2.imshow(self.winname, frame)
                    cv2.waitKey(1)
                if self.clic_on_window:
                    cv2.setMouseCallback(self.winname, self.mouse_callback)
        self.cam.stopSequenceAcquisition()
        camera_unload(self.cam)
        self.cam.reset()

    def save_img(self):
        path = './{i}/screenshots/screenshot{n}'.format(i=self.controller, n=self.n_img)
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as exc:
                # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        img = self.frame*255
        cv2.imwrite('./{i}/screenshots/screenshot{n}.jpg'.format(i=self.controller, n=self.n_img), img)
        self.n_img += 1
        pass

    def switch_mouse_callback(self):
        self.mouse_callback ^= 1

    def stop(self):
        self.show = False
