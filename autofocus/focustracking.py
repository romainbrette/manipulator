'''
Tracking algorithm to keep the tip in focus during a move
Use the template matching method to focus
'''

from template_focus import *
from template_matching import *
from get_img import *


__all__ = ['focus_track']

def focus_track(devtype, microscope, arm, template, step, axis, estim=0, cap=None):
    """
    Focus after a move of the arm
    """
    _, img = getImg(devtype, microscope, cv2cap=cap)
    _, _, initloc = templatematching(img, template)

    if step == 2:
        arm.relative_move(step, axis)
        _, estim_temp, estim_loc = focus(devtype, microscope, template, cap, 2)
    else:
        arm.relative_move(step, axis)
        if devtype == 'SM5':
            microscope.setRelativePosition(estim*step)
        else:
            microscope.relative_move(estim*step, 2)
        _, estim_temp, estim_loc = focus(devtype, microscope, template, cap, 1)
    print float(estim_temp)
    estim += float(estim_temp)/step
    print estim
    estim_loc = [(estim_loc[i] - initloc[i])/step for i in range(2)]

    return estim, estim_loc