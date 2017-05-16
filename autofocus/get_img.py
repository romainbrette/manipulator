"""
Read the frame of a video capture at given absolute height of the microscope
Encode the frame to make it usable for some functions (cornerHarris)
"""

import cv2
import numpy as np
import time

__all__ = ['getImg']


def getImg(devtype, microscope, z=None, cv2cap=None):

    """
    get an image from the microscope at given height z
    :param devtype: type of device controller, either 'SM5' or 'SM10'.
    :param microscope: class instance controlling the microscope
    :param z: desired absolute height of the microscope
    :param cv2cap: video capture from cv2, used when devtype='SM10'
    :return frame: image taken directly from the video capture
            img: frame encoded in 8bits, necessary for some functions as cornerHarris()
    """

    frame, img = 0, 0
    if devtype == 'SM5':

        # Move the microscope if an height has been specify
        if z:
            microscope.setPosition(z)

        # Capture frame

        if microscope.getRemainingImageCount() > 0:
            cam = microscope.getLastImage()
            # Conversion so the frame can be used with openCV imshow()
            frame = cam.view(dtype=np.uint8)
            img = cam

    elif devtype == 'SM10':

        # Move the microscope if an height has been specify
        if z:
            cv2cap.release()
            microscope.absolute_move(z, 2)
            #time.sleep(1)
            cv2cap = cv2.VideoCapture(0)

        # Capture frame
        ret, frame = cv2cap.read()

        # frame has to be encoded to an usable image to use tipdetect()
        _, img = cv2.imencode('.jpg', frame)
        img = cv2.imdecode(img, 0)

    else:
        raise TypeError('Unknown device. Should be either "SM5" or "SM10".')

    return frame, img, cv2cap


if __name__ == '__main__':
    from serial import SerialException
    from devices import *
    from Hamamatsu_camera import *

    try:
        dev = LuigsNeumann_SM5('COM3')
    except SerialException:
        print "L&N SM-5 not found. Falling back on fake device."
        dev = FakeDevice()

    mmc = camera_init()
    mmc.startContinuousSequenceAcquisition(1)
    cv2.namedWindow('Camera')
    while 1:
        buffer = mmc.getLastImage()
        frame, img = getImg('SM5', mmc)
        cv2.imshow("Camera", frame)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break

    mmc.stopSequenceAcquisition()
    camera_unload(mmc)
    mmc.reset()
    cv2.destroyAllWindows()
    del dev