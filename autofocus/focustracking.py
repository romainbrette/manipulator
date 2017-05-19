'''
Tracking algorithm to keep the tip in focus during a move
Use the template matching method to focus
'''

from template_focus import *
from template_matching import *
from get_img import *
import cv2


__all__ = ['focus_track']


def focus_track(devtype, microscope, arm, template, step, axis, alpha, um_px, estim=0, estim_loc=(0.,0.), cap=None):
    """
    Focus after a move of the arm
    """

    if devtype == 'SM5':
        pos = microscope.getPosition()
    else:
        pos = microscope.position(2)
    frame, img, cap = getImg(devtype, microscope, pos, cap)

    # Get initial location of the tip
    _, _, initloc = templatematching(img, template)

    # Move the arm
    arm.relative_move(step, axis)
    frame, img, cap = getImg(devtype, microscope, pos, cap)
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

    # Move the platform to center the tip
    for i in range(2):
        microscope.relative_move(alpha[i]*estim_loc[i]*step, i)

    # Update the frame. Must be the next image

    frame, img, cap = getImg(devtype, microscope, pos + estim * step, cv2cap=cap)
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)
    # Focus around the estimated focus height
    _, estim_temp, loc, frame, cap = focus(devtype, microscope, template, cap, 2)
    # MOVE THE PLATFORM TO COMPENSATE ERROR AND UPDATE FRAME
    for i in range(2):
        microscope.relative_move(alpha[i]*(loc[i] - initloc[i])*um_px , i)

    frame, img, cap = getImg(devtype, microscope, pos + estim * step + estim_temp, cv2cap=cap)
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

    '''
        if devtype == 'SM5':
            microscope.setRelativePosition(estim*step)
        else:
            # PROBLEM WITH MICROSCOPE IF RELATIVE MOVE IS -8
            if estim*step != -8:
                microscope.relative_move(estim*step, 2)
            else:
                for i in range(2):
                    microscope.relative_move(-4, 2)
    '''

    # Update the estimated move to do for a move of 1 um of the arm
    estim += float(estim_temp)/float(step)
    print estim
    loc = [estim_loc[i] + (loc[i]-initloc[i])*um_px/float(step) for i in range(2)]

    return estim, loc, frame, cap