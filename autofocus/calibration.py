import cv2
from get_img import *
from focustracking import *
from time import sleep

__all__ = ['calibrate']


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
