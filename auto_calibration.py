"""
Camera GUI for LuigsNeumann_SM10 and SM5 to make an auto-calibration of an arm
Requires OpenCV
To begin the calibration, the user shall put the tip on focus at the center of the displayed red cross and press 'b'
after calibration, press 'p' to center the tip in any position of the microscope
Auto focus using template matching by pressing 'f'
Quit with key 'q'
"""

from autofocus import *
from numpy import matrix
from numpy.linalg import inv
import numpy as np
from time import sleep

# Type of used controller, either 'SM5' or 'SM10 for L&N SM-5 or L&N SM-10
devtype = 'SM5'

# Initializing the device, camera and microscope according to the used controller
dev, microscope, arm, cam = init_device(devtype, 'dev1')

# Exposure for the camera when using MicroManager
exposure = 15

# Naming the live camera window
cv2.namedWindow('Camera', flags=cv2.WINDOW_NORMAL)

# Booleans for template, calibration
template = 0
calibrating = 0
calibrate_succeeded = 0

# Actual step in calibration
step = 0

# Maximum number of steps to do
maxdist = 600

# Initial displacement of the arm to do, in um
first_step = 2.

# Initial estimation (displacement microscope)/(displ moved axis), in um/um
estim = [0., 0., 0.]

# Rotation of the platform compared to the camera
alpha = matrix('0. 0.; 0. 0.')

# Initializing transformation matrix (Jacobian)
M = matrix('0. 0. 0.; 0. 0. 0.; 0. 0. 0.')
M_inv = M

x_init, y_init = 0, 0
um_px = 0.
init_pos_m = [0., 0., 0.]
init_pos_a = [0., 0., 0.]
template_loc = [0., 0.]

# GUI loop with image processing
while 1:

    # Capture a frame from video
    buf = cam.getLastImage()

    frame = get_img(microscope, cam)

    # Keyboards controls:
    # 'q' to quit,
    # 'f' for autofocus,
    # 'b' to begin calibration
    # 'p' to center the tip, after calibration
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

    if key & 0xFF == ord('+'):
        if devtype == 'SM5':
            exposure += 1
            cam.setExposure(exposure)

    if key & 0xFF == ord('-'):
        if devtype == 'SM5':
            exposure -= 1
            cam.setExposure(exposure)

    if key & 0xFF == ord('f'):
        if isinstance(template, list):
            _, _, _, frame = focus(microscope, template, cam)
            print 'Auto-focus done.'
        else:
            print 'Template image has not been taken yet.'

    if key & 0xFF == ord('b'):
        calibrating ^= 1
        calibrate_succeeded = 0
        template = 0
        step = 0

    if key & 0xFF == ord('p'):
        if calibrate_succeeded:
            pos = matrix('0.; 0.; 0.')
            for i in range(3):
                pos[i, 0] = microscope.position(i) - init_pos_m[i]

            X = M_inv*pos
            for i in range(3):
                arm.absolute_move(init_pos_a[i]+X[i], i)
        else:
            print 'Calibration must be done beforehand.'

    if key & 0xFF == ord('a'):
        microscope.relative_move(-100, 0)

    if key & 0xFF == ord('r'):
        if calibrate_succeeded:
            # Recalibration to change pipette
            init_pos_m, init_pos_a = pipettechange(microscope, arm, M, template, template_loc, x_init, y_init, um_px,
                                                   alpha, cam)

    if calibrating:
        if step == 0:
            # Saving initial position of the arm and the microscope
            init_pos_a = [arm.position(i) for i in range(3)]
            init_pos_m = [microscope.position(i) for i in range(3)]

            # Get a series of template images for auto focus
            template, template_loc = get_template_series(microscope, 5, cam)

            # Saving initial position of the tip on the screen
            _, _, loc = templatematching(frame, template[len(template)/2])
            x_init, y_init = loc[:2]

            # Getting the ratio um per pixels and the rotation of the platform

            alpha, um_px = calibrate_platform(microscope, template, x_init, y_init, cam)

            step += 1

            print 'Calibrated platform'

        elif step == 1:
            # calibrate arm y axis
            M, stop, frame = calibrate(microscope, arm, M, init_pos_m, init_pos_a, 0, first_step, maxdist, template,
                                       alpha, um_px, cam)

            if stop:
                calibrating = 0
            else:
                print 'Calibrated x axis'
                step += 1

        elif step == 2:
            # calibrate arm y axis
            M, stop, frame = calibrate(microscope, arm, M, init_pos_m, init_pos_a, 1, first_step, maxdist, template,
                                       alpha, um_px, cam)

            if stop:
                calibrating = 0
            else:
                print 'Calibrated y axis'
                step += 1

        elif step == 3:
            # calibrate arm z axis
            M, stop, frame = calibrate(microscope, arm, M, init_pos_m, init_pos_a, 2, first_step, maxdist, template,
                                       alpha, um_px, cam)

            if stop:
                calibrating = 0
            else:
                print 'Calibrated z axis'
                step += 1

        elif step == 4:

            print M
            M_inv = inv(M)
            print M_inv
            calibrating = 0
            calibrate_succeeded = 1
            print 'Calibration finished'

    # Our operations on the frame come here
    if isinstance(frame, np.ndarray):
        if not isinstance(template, list):
            # Display a rectangle where the template will be taken
            frame = disp_template_zone(frame)

        # Display a red centered cross
        frame = disp_centered_cross(frame)

        # Parameters for mouse callbacks
        param = {'calibrated': calibrate_succeeded, 'mat': M_inv, 'x_init': x_init, 'y_init': y_init, 'um_px': um_px,
                 'mic': microscope, 'arm': arm, 'init_mic': init_pos_m, 'init_arm': init_pos_a, 'alpha': alpha,
                 'loc': template_loc}

        cv2.imshow('Camera', frame)
        cv2.setMouseCallback('Camera', clic_position, param)
        cv2.waitKey(1)

# When everything done, release the capture
stop_device(dev, microscope, cam)
