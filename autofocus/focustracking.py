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

    # Get initial location of the tip
    _, _, initloc = templatematching(img, template)

    # Move the arm
    arm.relative_move(step, axis)

    # Update the frame. Must be the next image
    pos = microscope.position(2)
    frame, img, cap = getImg(devtype, microscope, pos, cv2cap=cap)
    cv2.imshow('Camera', frame)
    print 'arm moved'
    cv2.waitKey(1)

    # focusing
    if estim == 0:
        # No estimation has been made
        _, estim_temp, estim_loc, frame, cap = focus(devtype, microscope, template, cap, 3)
        cv2.imshow('Camera', frame)
        cv2.waitKey(1)
    else:
        # Estimation has been made, move the microscope to the estimated focus height
        if devtype == 'SM5':
            microscope.setRelativePosition(estim*step)
        else:
            # PROBLEM WITH MICROSCOPE IF RELATIVE MOVE IS -8
            if estim*step != -8:
                microscope.relative_move(estim*step, 2)
            else:
                for i in range(2):
                    microscope.relative_move(-4, 2)

        print 'micro moved'

        # Update the frame after moving the microscope
        pos = microscope.position(2)
        frame, img, cap = getImg(devtype, microscope, pos, cv2cap=cap)
        cv2.imshow('Camera', frame)
        cv2.waitKey(1)

        # Focus around the estimated focus height
        _, estim_temp, estim_loc, frame, cap = focus(devtype, microscope, template, cap, 2)
        cv2.imshow('Camera', frame)
        cv2.waitKey(1)

    # Update the estimated move to do for a move of 1 um of the arm
    estim += float(estim_temp)/float(step)

    # Update the displacement in x and y of the tip for a move of 1 um of the arm, in px/um
    estim_loc = [float(estim_loc[i] - initloc[i])/float(step) for i in range(2)]

    return estim, estim_loc, frame, cap