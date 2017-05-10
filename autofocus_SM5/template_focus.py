"""
Autofocusing on the tip using template matching
First user must put the tip on focus to get the template
Template matching is not scale nor rotation invariant
"""

__all__ = ['focus']

from camera_init import *
from template_matching import *
from get_img import *

def focus(devtype, microscope, template, cap=None):

    if devtype == 'SM5':
        current_z = microscope.getPosition()
    elif devtype== 'SM10':
        current_z = microscope.position(2)
    else:
        raise TypeError('Unknown device. Should be either "SM5" or "SM10".')

    vals = []
    location = []

    for i in range(7):
        _, img = getImg(devtype, microscope, current_z - i + 3, cap)
        res, val, loc = templatematching(img, template)
        location += [loc]
        if res:
            vals += [val]
        else:
            vals += [0]

    maxval = max(vals)
    if maxval != 0:
        locate = location[vals.index(maxval)]
        microscope.absolute_move(current_z - locate + 3, 2)
        x, y = locate[:2]
    else:
        raise ValueError('The template image has not been detected.')

    return maxval, x, y