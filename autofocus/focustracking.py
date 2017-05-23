"""
Tracking algorithm to keep the tip in focus during a move
Use the template matching method to focus
"""

from focus_template_series import *
from template_matching import *
from get_img import *
import cv2


__all__ = ['focus_track']


def focus_track(devtype, microscope, arm, template, step, axis, alpha, um_px, estim=0, estim_loc=(0., 0.), cap=None):
    """
    Focus after a move of the arm
    """

    if devtype == 'SM5':
        pos = microscope.getPosition()
    else:
        pos = microscope.position(2)

    # Update frame just in case
    frame = getImg(devtype, microscope, cv2cap=cap, update=1)

    # Get initial location of the tip
    _, _, initloc = templatematching(frame, template[len(template)/2])

    # Move the arm
    arm.relative_move(step, axis)
    frame = getImg(devtype, microscope, cv2cap=cap, update=1)
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

    # Move the platform to center the tip
    for i in range(2):
        microscope.relative_move(alpha[i]*estim_loc[i]*step, i)

    # Update the frame.
    frame = getImg(devtype, microscope, cv2cap=cap, update=1)
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

    # Move the microscope
    frame = getImg(devtype, microscope, pos + estim * step, cv2cap=cap)
    cv2.imshow('Camera', frame)
    cv2.waitKey(5)

    # Focus around the estimated focus height
    _, estim_temp, loc, frame = focus(devtype, microscope, template, cap)

    # Move the platform for compensation
    for i in range(2):
        microscope.relative_move(alpha[i]*(loc[i] - initloc[i])*um_px, i)

    #Update frame
    frame = getImg(devtype, microscope, cv2cap=cap, update=1)
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

    # Update the estimated move to do for a move of 1 um of the arm
    estim += float(estim_temp)/float(step)
    loc = [estim_loc[i] + (loc[i]-initloc[i])*um_px/float(step) for i in range(2)]

    return estim, loc, frame
