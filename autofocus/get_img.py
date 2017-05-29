"""
Read the frame of a video capture at given absolute height of the microscope
Encode the frame to make it usable for some functions (cornerHarris)
"""

import cv2
import numpy as np

__all__ = ['getImg']


def getImg(devtype, microscope, z=None, cv2cap=None, update=0):

    """
    get an image from the microscope at given height z
    :param devtype: type of device controller, either 'SM5' or 'SM10'.
    :param microscope: class instance controlling the microscope
    :param z: desired absolute height of the microscope
    :param cv2cap: video capture from cv2, used when devtype='SM10'
    :param update: indicating if the user wants the next frame or not 
    :return frame: image taken directly from the video capture
    """

    frame = 0
    if devtype == 'SM5':

        # Move the microscope if an height has been specify
        if z:
            microscope.absolute_move(z, 2)
            cv2.waitKey(1000)
            update = 1

        # Capture frame

        if cv2cap.getRemainingImageCount() > 0:

            frame = cv2cap.getLastImage()
            frame = np.float32(frame/(1.0*frame.max()))

    elif devtype == 'SM10':

        # Move the microscope if an height has been specify
        if z:
            microscope.absolute_move(z, 2)
            update = 1

        #if update:
        #    _, frame = cv2cap.retrieve()

        # Capture frame

        #ret, frame = cv2cap.read()
        if cv2cap.getRemainingImageCount() > 0:

            frame = cv2cap.getLastImage()
            frame = np.float32(frame/(1.0*frame.max()))

    else:
        raise TypeError('Unknown device. Should be either "SM5" or "SM10".')

    frame = cv2.flip(frame, 2)

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
        buffer = mmc.getLastImage()
        frame = getImg('SM5', mmc)
        cv2.imshow("Camera", frame)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break

    mmc.stopSequenceAcquisition()
    camera_unload(mmc)
    mmc.reset()
    cv2.destroyAllWindows()
    del dev