"""
Autofocusing on the tip using template matching
First user must put the tip on focus to get the template
Template matching is not scale nor rotation invariant
NOT USED ANYMORE
"""

from autofocus.template_matching import *
from autofocus.get_img import *
import cv2

__all__ = ['dfocus']


def dfocus(devtype, microscope, template, cv2cap=None, rng=1):
    """
    Autofocus by searching the best template match in the image around the current height
    :param devtype: type of used controller
    :param microscope: device controlling the microscope
    :param template: template image to look for
    :param cv2cap: video capture from cv2, unnecessary if devtype='SM5' 
    :param rng: range of search in um
    """

    # Getting the microscope height according to the used controller
    if devtype == 'SM5':
        current_z = microscope.Position(2)
    elif devtype == 'SM10':
        current_z = microscope.position(2)
    else:
        raise TypeError('Unknown device. Should be either "SM5" or "SM10".')

    # Tabs of maxval and their location during the process
    vals = []
    locs = []

    # Getting the maxvals and their locations at +- rng um, 1um steps, around the current height
    for i in range(rng*2+1):

        height = current_z + (rng - i)
        frame = get_img(microscope, cv2cap, height)
        res, val, loc = templatematching(frame, template)
        cv2.imshow('Camera', frame)
        cv2.waitKey(1)
        locs += [loc]
        if res:
            # Template has been detected
            vals += [val]
        else:
            # Template has not been detected, val set at 0
            vals += [0]

    print vals
    # Search of the highest value, indicating that focus has been achieved
    maxval = max(vals)

    if maxval != 0:
        # Template has been detected at least once, setting the microscope at corresponding height
        index = vals.index(maxval)
        loc = locs[index]
        focus_height = current_z + (rng - index)
        frame, _ = get_img(microscope, cv2cap, focus_height)
        cv2.imshow('Camera', frame)
        cv2.waitKey(1)
        dep = (rng - index)
    else:
        # Template has never been detected, focus can not be achieved
        raise ValueError('The template image has not been detected.')

    return maxval, dep, loc, frame
