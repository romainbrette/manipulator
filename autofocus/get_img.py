"""
Read the frame of a video capture at given height of the microscope
Encode the frame to make it usable for some functions (cornerHarris)
"""

import cv2

__all__ = ['getImg']


def getImg(cap, microscope=None, z=None):

    '''
    get an image from the microscope at given height z
    :param cap: capture from a cv2.VideoCapture
    :param z: desired height of the microscope
    :param microscope: device instance
    '''

    # Move the microscope if an height has been specify
    if z:
        microscope.absolute_move(z, 2)

    # Capture frame
    ret, frame = cap.read()

    # frame has to be encoded to an usable image to use tipdetect()
    _, img = cv2.imencode('.jpg', frame)

    return frame, cv2.imdecode(img, 0)


if __name__ == '__main__':
    from serial import SerialException
    from devices import *

    try:
        dev = LuigsNeumann_SM10()
    except SerialException:
        print "L&N SM-10 not found. Falling back on fake device."
        dev = FakeDevice()

    cap = cv2.VideoCapture(0)
    microscope = XYZUnit(dev, [7, 8, 9])
    frame, img = getImg(cap, microscope)
    cap.release()
    del dev