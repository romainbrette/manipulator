"""
Autofocusing on the tip using template matching
First user must put the tip on focus to get the template
Template matching is not scale nor rotation invariant
"""

__all__ = ['focus']

import cv2
from devices import *
from template_matching import *
from get_img import *

def focus(cap, template, microscope):

    current_z = microscope.position(2)
    vals = []
    location = []

    for i in range(7):
        microscope.absolute_move(current_z - i + 3, 2)
        _, img = getImg(cap)
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

    return x, y