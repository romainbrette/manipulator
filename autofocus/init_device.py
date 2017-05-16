import cv2
from devices import *
from serial import SerialException
from Hamamatsu_camera import *

def init_device(devtype):
    if devtype == 'SM5':
        try:
            dev = None
            cap = None
            microscope = camera_init()
            microscope.startContinuousSequenceAcquisition(1)
        except Warning:
            raise SerialException("L&N SM-5 not found.")
    elif devtype == 'SM10':
        try:
            dev = LuigsNeumann_SM10()
            cap = cv2.VideoCapture(0)
            microscope = XYZUnit(dev, [7, 8, 9])
        except SerialException:
            raise SerialException("L&N SM-10 not found.")
    else:
        raise SerialException("No supported device detected")

    return dev, microscope, cap