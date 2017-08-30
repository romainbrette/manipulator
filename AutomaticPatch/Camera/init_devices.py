from devices import *
from serial import SerialException

__all__ = ['init_device']


def init_device(devtype, armdev):
    """
    Initialization of microscope and arm
    :param devtype: controller
    :param armdev: devices controlling the arm
    :return: 
    """

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

    if armdev == 'dev1':
        arm = XYZUnit(dev, [1, 2, 3])
    elif armdev == 'dev2':
        arm = XYZUnit(dev, [4, 5, 6])
    elif armdev == 'Arduino':
        try:
            # arduino = appel classe manipulateur arduino
            #arm = XYZUnit(arduino, [1, 2, 3])
            arm = 0
        except SerialException:
            raise SerialException("Arduino not found.")
    else:
        raise NameError('Unknown device for arm control.')

    # Adjust ramp length for accuracy
    microscope.set_ramp_length([0, 1, 2], 3)
    arm.set_ramp_length([0, 1, 2], 3)

    return dev, microscope, arm
