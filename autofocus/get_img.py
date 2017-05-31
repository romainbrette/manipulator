"""
Read the last frame taken by a camera at given absolute height of the microscope
"""

import cv2
import numpy as np
from time import sleep

__all__ = ['get_img']


def get_img(microscope, cam, z=None):

    """
    get an image from the microscope at given height z
    :param microscope: class instance controlling the microscope
    :param z: desired absolute height of the microscope
    :param cam: micro manager camera
    :return frame: image taken from camera
    """

    # Move the microscope if an height has been specify
    if z:
        microscope.absolute_move(z, 2)
        sleep(1)

    # capture frame

    if cam.getRemainingImageCount() > 0:

        frame = cam.getLastImage()
        frame = np.float32(frame/(1.0*frame.max()))

    if isinstance(frame, np.ndarray):
        frame = cv2.flip(frame, 2)
    else:
        raise TypeError('Could not read image from camera.')

    return frame


if __name__ == '__main__':
    from serial import SerialException
    from devices import *
    from Hamamatsu_camera import *

    try:
        dev = LuigsNeumann_SM5('COM3')
    except SerialException:
        print "L&N SM-5 not found. Falling back on fake device."
        dev = FakeDevice()

    mmc = camera_init('SM5')
    mmc.startContinuousSequenceAcquisition(1)
    cv2.namedWindow('Camera')
    while 1:
        buf = mmc.getLastImage()
        img = get_img('SM5', mmc)
        cv2.imshow("Camera", img)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break

    mmc.stopSequenceAcquisition()
    camera_unload(mmc)
    mmc.reset()
    cv2.destroyAllWindows()
    del dev
