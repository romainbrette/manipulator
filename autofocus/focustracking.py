"""
Tracking algorithm to keep the tip in focus during a move
Use the template matching method to focus
"""

from focus_template_series import *
from template_matching import *
from get_img import *
from numpy import matrix
from numpy.linalg import inv
import cv2
from time import sleep


__all__ = ['focus_track']


def focus_track(microscope, arm, template, step, axis, alpha, um_px, estim, cam):
    """
    Focus after a move of the arm
    """

    pos = microscope.position(2)
    apos = arm.position(axis)
    # Update frame just in case
    frame = get_img(microscope, cam)

    # Get initial location of the tip
    _, _, initloc = templatematching(frame, template[len(template)/2])

    # Move the arm
    arm.relative_move(step, axis)
    sleep(1)
    frame = get_img(microscope, cam)
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)
    print step
    print arm.position(axis) - apos

    # Move the platform to center the tip
    delta = matrix('{a}; {b}'.format(a=estim[0]*step, b=estim[1]*step))
    move = inv(alpha)*delta
    for i in range(2):
        microscope.relative_move(move[i, 0], i)
    sleep(1)

    # Update the frame.
    frame = get_img(microscope, cam)
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

    # Move the microscope
    frame = get_img(microscope, cam, pos + estim[2] * step)
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

    # Focus around the estimated focus height
    _, estim_temp, loc, frame = focus(microscope, template, cam)

    # Move the platform for compensation
    delta = matrix('{a}; {b}'.format(a=(initloc[0] - loc[0])*um_px, b=(initloc[1] - loc[1])*um_px))
    move = inv(alpha) * delta
    for i in range(2):
        microscope.relative_move(move[i, 0], i)

    sleep(1)

    # Update frame
    frame = get_img(microscope, cam)
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

    # Update the estimated move to do for a move of 1 um of the arm
    estim[2] += float(estim_temp)/float(step)
    for i in range(2):
        estim[i] += (initloc[i] - loc[i])*um_px/float(step)

    return estim, frame
