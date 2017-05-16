'''
Tracking algorithm to keep the tip in focus during a move
Use the template matching method to focus
'''

from template_focus import *
from template_matching import *
from get_img import *


__all__ = ['focus_track']

def focus_track(devtype, microscope, arm, img, template, step, axis, estim=0, cap=None):
    """
    Focus after a move of the arm
    """
    _, _, initloc = templatematching(img, template)

    if step == 2:
        arm.relative_move(step, axis)
        _, estim_temp, estim_loc, frame, cap = focus(devtype, microscope, template, cap, 3)
    else:
        arm.relative_move(step, axis)
        if devtype == 'SM5':
            microscope.setRelativePosition(estim*step)
        else:
            microscope.relative_move(estim*step, 2)
        _, estim_temp, estim_loc, frame, cap = focus(devtype, microscope, template, cap, 3)

    estim += float(estim_temp)/float(step)
    estim_loc = [float(estim_loc[i] - initloc[i])/float(step) for i in range(2)]

    return estim, estim_loc, frame, cap