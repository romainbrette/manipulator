"""
Autofocusing on the tip using template matching
First user must put the tip on focus to get the template
Template matching is not scale nor rotation invariant
"""

__all__ = ['focus']

from template_matching import *
from get_img import *
import cv2



def focus(devtype, microscope, template, cv2cap=None):
    """
    Autofocus by searching the best template match in the image around the current height
    :param devtype: type of used controller
    :param microscope: device controlling the microscope
    :param template: tab of template images to look for
    :param cv2cap: video capture from cv2, unnecessary if devtype='SM5' 
    :param step: step length made if the arm is moving (for quicker tracking)
    """

    # Getting the microscope height according to the used controller
    if devtype == 'SM5':
        current_z = microscope.getPosition()
    elif devtype == 'SM10':
        current_z = microscope.position(2)
    else:
        raise TypeError('Unknown device. Should be either "SM5" or "SM10".')

    frame, img, cv2cap = getImg(devtype, microscope, current_z, cv2cap)
    # Tabs of maxval and their location during the process
    vals = []
    locs = []

    # Getting the maxvals and their locations at +- rng um, 1um steps, around the current height
    for i in template:

        res, val, loc = templatematching(img, i)
        locs += [loc]

        if res:
            # Template has been detected
            vals += [val]
        else:
            # Template has not been detected, val set at 0
            vals += [0]
        '''
        if val > 0.95:
            maxval = val
            dep = rng - i
            #print len(vals)
            return maxval, dep, loc, frame
        '''

    # Search of the highest value, indicating which template image match the best the current image
    maxval = max(vals)

    if maxval != 0:
        # At least one template has been detected, setting the microscope at corresponding height
        index = vals.index(maxval)
        loc = locs[index]
        focus_height = current_z + len(template)/2 - index
        frame, _, cv2cap = getImg(devtype, microscope, focus_height, cv2cap)
        cv2.imshow('Camera', frame)
        cv2.waitKey(1)
        dep = len(template)/2 - index
    else:
        # No template has been detected, focus can not be achieved
        raise ValueError('The template image has not been detected.')

    return maxval, dep, loc, frame, cv2cap
