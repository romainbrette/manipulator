"""
Autofocusing on the tip using template matching
First user must put the tip on focus to get the template
Template matching is not scale nor rotation invariant
"""

__all__ = ['focus']

from Hamamatsu_camera import *
from template_matching import *
from get_img import *
from scipy.optimize import minimize_scalar, minimize
from math import fabs

def focus(devtype, microscope, template, cv2cap=None):
    """
    Autofocus by searching the best template match in the image around the current height
    :param devtype: type of used controller
    :param microscope: device controlling the microscope
    :param template: template image to look for
    :param cv2cap: video capture from cv2, unnecessary if devtype='SM5' 
    """

    # Getting the microscope height according to the used controller
    if devtype == 'SM5':
        current_z = microscope.getPosition()
    elif devtype== 'SM10':
        current_z = microscope.position(2)
    else:
        raise TypeError('Unknown device. Should be either "SM5" or "SM10".')
    """
    # minimize() quicker but less performant 
    fun = lambda x: -templatematching(getImg(devtype, microscope, x, cap)[1], template)[1]
    cons = ({'type': 'ineq', 'fun': lambda x: 4 - fabs(x - current_z)})
    minimize(fun, current_z, method='COBYLA', constraints=cons, tol=0.9, options={'maxiter': 20, 'rhobeg':3})
    res, maxval, maxloc = templatematching(getImg(devtype, microscope, cv2cap=cap)[1], template)
    x, y = maxloc[:2]
    """

    # Tabs of maxval and their locations during the process
    vals = []
    location = []

    # Getting the maxval and their locations at +-4um, 1um steps, around the current height
    for i in range(9):
        _, img = getImg(devtype, microscope, current_z - i + 4, cv2cap)
        res, val, loc = templatematching(img, template)
        location += [loc]
        if res:
            # Template has been detected
            vals += [val]
        else:
            # Template has not been detected, maxval set at 0
            vals += [0]

    # Search of the highest value, indicating that focus has been achieved
    maxval = max(vals)

    if maxval != 0:
        # Template has been detected at least once, setting the microscope at corresponding height
        index = vals.index(maxval)
        locate = location[index]
        _, img = getImg(devtype, microscope, current_z - index + 4, cv2cap)
        x, y = locate[:2]
    else:
        # Template has never been detected, focus can not be achieved
        raise ValueError('The template image has not been detected.')

    pass