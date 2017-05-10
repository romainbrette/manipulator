"""
Autofocusing on the tip using template matching
First user must put the tip on focus to get the template
Template matching is not scale nor rotation invariant
"""

__all__ = ['focus']

from camera_init import *
from template_matching import *
from get_img import *
from scipy.optimize import minimize_scalar, minimize
from math import fabs

def focus(devtype, microscope, template, cap=None):

    if devtype == 'SM5':
        current_z = microscope.getPosition()
    elif devtype== 'SM10':
        current_z = microscope.position(2)
    else:
        raise TypeError('Unknown device. Should be either "SM5" or "SM10".')
    """
    fun = lambda x: -templatematching(getImg(devtype, microscope, x, cap)[1], template)[1]
    cons = ({'type': 'ineq', 'fun': lambda x: 4 - fabs(x - current_z)})
    minimize(fun, current_z, method='COBYLA', constraints=cons, tol=0.9, options={'maxiter': 20, 'rhobeg':3})
    res, maxval, maxloc = templatematching(getImg(devtype, microscope, cv2cap=cap)[1], template)
    x, y = maxloc[:2]
    """

    vals = []
    location = []

    for i in range(9):
        _, img = getImg(devtype, microscope, current_z - i + 4, cap)
        res, val, loc = templatematching(img, template)
        location += [loc]
        if res:
            vals += [val]
        else:
            vals += [0]

    maxval = max(vals)
    if maxval != 0:
        index = vals.index(maxval)
        locate = location[index]
        microscope.absolute_move(current_z - index + 4, 2)
        x, y = locate[:2]
    else:
        raise ValueError('The template image has not been detected.')

    return maxval, x, y