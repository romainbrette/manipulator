import cv2
from get_img import *
from focustracking import *
from time import sleep
from math import fabs
from template_matching import *
from focus_template_series import *
from numpy import matrix

__all__ = ['calibrate', 'pipettechange']


def calibrate(microscope, arm, mat, init_pos_m, init_pos_a, axis, first_step, maxdistance, template, alpha, um_px, cam):

    estim = [0., 0., 0.]
    totaldistance = 0
    step = first_step
    stop = 0
    calibrated = 0

    frame = get_img(microscope, cam)
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

    while not calibrated:

        cv2.imshow('Camera', frame)
        key = cv2.waitKey(1)

        if key & 0xFF == ord('q'):
            stop = 1
            break

        if totaldistance < maxdistance:

            # calibrate arm axis using exponential moves:
            # moves the arm, recenter the tip and refocus.
            # displacements are saved
            estim, frame = focus_track(microscope, arm, template, step, axis, alpha, um_px, estim, cam)
            totaldistance += step
            step *= 2

        else:

            # When cali_bration is finished:
            # Accuracy along z axis = total displacement +- 1um = 2**(maxnstep-1)-2 +-1

            # Update transformation matrix (Jacobian)
            for i in range(3):
                estim[i] = (init_pos_m[i] - microscope.position(i)) / (init_pos_a[axis] - arm.position(axis))

            mat[0, axis] = estim[0]
            mat[1, axis] = estim[1]
            mat[2, axis] = estim[2]

            # Resetting position of arm and microscope so no error gets to the next axis calibration
            for i in range(3):
                arm.absolute_move(init_pos_a[i], i)
                microscope.absolute_move(init_pos_m[i], i)

            sleep(2)

            # Update the frame
            frame = get_img(microscope, cam)
            cv2.imshow('Camera', frame)
            cv2.waitKey(10)

            calibrated = 1

    return mat, stop, frame


def pipettechange(microscope, arm, mat, template, template_loc, x_init, y_init, um_px, alpha, cam):

    """
    Change pipette & recalibration
    :param microscope: 
    :param arm: 
    :param mat: 
    :param template: 
    :param template_loc: 
    :param x_init: 
    :param y_init: 
    :param um_px: 
    :param alpha: 
    :param cam: 
    :return: 
    """
    ratio = fabs(mat[0, 0] / mat[1, 0])

    if ratio > 1:
        i = 0
    else:
        i = 1

    if template_loc[i] ^ (mat[i, 0] > 0):
        sign = -1
    else:
        sign = 1

    arm.relative_move(sign*5000000, 0)
    sleep(1)
    frame = get_img(microscope, cam)
    cv2.imshow('Camera', frame)
    cv2.waitKey(0)
    arm.relative_move(-sign*3000000, 0)
    sleep(1)
    frame = get_img(microscope, cam)
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

    while 1:
        arm.relative_move(100, 0)
        sleep(1)
        frame = get_img(microscope, cam)
        cv2.imshow('Camera', frame)
        cv2.waitKey(1)
        height, width = frame.shape[:2]
        ratio = 32
        img = frame[height/2-3*height/ratio:height/2+3*height/ratio, width/2-3*width/ratio:width/2+3*width/ratio]
        isin, val, loc = templatematching(img, template[len(template)/2])
        if isin:
            while val < 0.98:
                val, _, loc, frame = focus(microscope, template, cam)
                cv2.imshow('Camera', frame)
                cv2.waitKey(1)
            delta = matrix('{a}; {b}'.format(a=(x_init-loc[0])*um_px, b=(y_init-loc[1])*um_px))
            move = alpha*delta
            for i in range(2):
                arm.relative_move(move[i, 0], i)
            sleep(1)
            frame = get_img(microscope, cam)
            cv2.imshow('Camera', frame)
            cv2.waitKey(1)
            init_pos_a = [arm.position(i) for i in range(3)]
            init_pos_m = [microscope.position(i) for i in range(3)]
            break

    return init_pos_m, init_pos_a
