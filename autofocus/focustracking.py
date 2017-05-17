'''
Tracking algorithm to keep the tip in focus during a move
Use the template matching method to focus
'''

from template_focus import *
from template_matching import *
from get_img import *
import cv2


__all__ = ['focus_track']

def focus_track(devtype, microscope, arm, img, template, step, axis, estim=0, cap=None):
    """
    Focus after a move of the arm
    """
    _, _, initloc = templatematching(img, template)
    arm.relative_move(step, axis)
    frame, img, cap = getImg(devtype, microscope, cv2cap=cap)

    if step == 2:
        cv2.imwrite('Before.jpg', frame)
        _, estim_temp, estim_loc, frame, cap = focus(devtype, microscope, template, cap, 3)
        cv2.imwrite('First.jpg', frame)
    else:
        if devtype == 'SM5':
            microscope.setRelativePosition(estim*step)
        else:
            microscope.relative_move(estim*step, 2)

        frame, img, cap = getImg(devtype, microscope, cv2cap=cap)
        cv2.imwrite('before focus {t}.jpg'.format(t=step), frame)
        _, estim_temp, estim_loc, frame, cap = focus(devtype, microscope, template, cap, 3)
        cv2.imwrite('after focus {t}.jpg'.format(t=step), frame)

    estim += float(estim_temp)/float(step)
    print estim
    estim_loc = [float(estim_loc[i] - initloc[i])/float(step) for i in range(2)]

    return estim, estim_loc, frame, cap