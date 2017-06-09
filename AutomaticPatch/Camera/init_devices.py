from devices import *
from serial import SerialException
from camera import *

__all__ = ['init_device']


def init_device(devtype, armdev):

    if devtype == 'SM5':
        try:
            dev = LuigsNeumann_SM5('COM3')
            devmic = Leica()
            microscope = XYMicUnit(dev, devmic, [7, 8])
        except:
            raise SerialException("L&N SM-5 not found.")
    elif devtype == 'SM10':
        try:
            dev = LuigsNeumann_SM10()
            microscope = XYZUnit(dev, [7, 8, 9])
        except SerialException:
            raise SerialException("L&N SM-10 not found.")
    else:
        raise SerialException("No supported device detected")

    cam = camera_init(devtype)
    cam.startContinuousSequenceAcquisition(1)

    if armdev == 'dev1':
        arm = XYZUnit(dev, [1, 2, 3])
    elif armdev == 'dev2':
        arm = XYZUnit(dev, [4, 5, 6])
    else:
        raise NameError('Unknown device for arm control.')

    return dev, microscope, arm, cam
