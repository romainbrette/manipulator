"""
Focusing the tip using tipdetect
Work only if the tip is well detected at first
"""

from devices import *
from tipdetect import *
from get_img import *
from scipy.optimize import minimize_scalar, minimize
from math import fabs

__all__ = ['tipfocus']


def tipfocus(microscope, cap):
    '''
    Focus on the tip around the current height.
    The tip should be nearly in focus.
    '''

    # Optimizing the cornerHarris criterion from tip detection around +- 5um of the current microscope height
    # shall indicate focus on the tip
    #fun = lambda x: -(1e4*tip_detect(getImg(cap, microscope, x)[1])[2])**5

    #  Using the maximum value of Corner-Harris algorithm (minimize_scalar too long)
    #mini = current_z - 10
    #maxi = current_z + 10

    #minimize_scalar(fun, bounds=(mini, maxi), method='Bounded')

    current_z = microscope.position(2)
    #cons = ({'type': 'ineq', 'fun': lambda x: 2.5 - fabs(x - current_z)})

    #minimize(fun, current_z, method='COBYLA', constraints=cons, tol=0.9, options={'maxiter': 25, 'rhobeg':2})

    z = [tip_detect(getImg(cap, microscope, x + current_z - 3)[1])[2] for x in range(7)]
    focus = current_z + z.index(max(z)) - 3
    microscope.absolut_move(focus, 2)

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
    tipfocus(microscope, cap)
    cap.release()
    del dev