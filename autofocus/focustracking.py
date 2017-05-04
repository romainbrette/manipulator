'''
Tracking algorithm to keep the tip in focus during a move
'''

from focus import *
from math import fabs
from devices import *


__all__ = ['focus_track']

def focus_track(device, relative_move, axis, microscope, cap):
    '''
    continuously focusing the tip during a move
    :param device: device type to be moved
    :param relative_move: relative displacement to be made by device 
    :param axis: device's axis for the movement
    :param microscope: microscope device
    '''

    # Initial position of the device

    init = device.position(axis)

    # total distance traveled

    disp = 0

    # Making the move step-by-step

    step = relative_move/fabs(relative_move) * 10

    while fabs(disp) < fabs(relative_move):
        device.relative_move(step, axis)
        disp = device.position(axis) - init
        # for testing
        print disp
        tipfocus(microscope, cap)

    pass

if __name__ == '__main__':
    from serial import SerialException
    import cv2

    try:
        dev = LuigsNeumann_SM10()
    except SerialException:
        print "L&N SM-10 not found. Falling back on fake device."
        dev = FakeDevice()

    cap = cv2.VideoCapture(0)
    microscope = XYZUnit(dev, [7, 8, 9])
    device = XYZUnit(dev, [1, 2, 3])
    tipfocus(microscope, cap)
    focus_track(device, 50, 0, microscope)
    cap.release()
    del dev