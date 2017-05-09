"""
Read the frame of a video capture at given RELATIVE height of the microscope
Encode the frame to make it usable for some functions (cornerHarris)
"""

import cv2
import matplotlib.pyplot as plt
from camera_init import *
import time

__all__ = ['getImg']


def getImg(mmc, z=None):

    '''
    get an image from the microscope at given height z
    :param mmc: micro manager camera, see "camera" in "devices"
    :param z: desired RELATIVE height of the microscope
    :param microscope: device instance
    '''

    # Move the microscope if an height has been specify
    if z:
        mmc.setRelativePosition(z)

    # Capture frame
    mmc.snapImage()
    frame = mmc.getImage()
    #time.sleep(1)

    # frame has to be encoded to an usable image to use tipdetect()
    _, img = cv2.imencode('.jpg', frame)

    return frame, cv2.imdecode(img, 0)


if __name__ == '__main__':
    from serial import SerialException
    from devices import *

    try:
        dev = LuigsNeumann_SM5('COM3')
    except SerialException:
        print "L&N SM-5 not found. Falling back on fake device."
        dev = FakeDevice()

    mmc = camera_init()
    plt.ion()
    while 1:
        frame, img = getImg(mmc)
        #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        plt.imshow(frame, cmap='gray')
        plt.pause(0.05)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break
    camera_unload(mmc)
    cv2.destroyAllWindows()
    del dev