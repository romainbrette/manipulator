"""
Camera GUI for LuigsNeumann_SM10 and SM5 to make an auto-calibration of an arm
Requires OpenCV
To begin the calibration, the user shall put the tip on focus at the center of the displayed red cross and press 'b'
after calibration, press 'p' to center the tip in any position of the microscope (with some accuracy)
Auto focus using template matching by pressing 'f'
Quit with key 'q'
"""

from autofocus import *
from numpy import matrix
from numpy.linalg import inv

# Type of used controller, either 'SM5' or 'SM10 for L&N SM-5 or L&N SM-10
devtype = 'SM5'

# Initializing the device, camera and microscope according to the used controller
dev, microscope, cap = init_device(devtype)

exposure = 15

# Device controlling the used arm and microscope
arm = XYZUnit(dev, [1, 2, 3])

# Naming the live camera window
cv2.namedWindow('Camera', flags=cv2.WINDOW_NORMAL)

# Booleans for template, calibration
template = 0
calibrate = 0
calibrate_succeeded = 0

# Actual step in calibration
step = 0

# Number of steps made for displacements of the arm during calibration
nstep = 1

# Maximum number of steps to do
maxnstep = 8

# Initial displacement of the arm to do, in um
track_step = 2.

# Initial estimation (displacement microscope)/(displ moved axis), in um/um
estim = [0., 0., 0.]

# Orientation
alpha = [-1., 1., 1.]

# Initializing transformation matrix (Jacobian)
M = matrix('0. 0. 0.; 0. 0. 0.; 0. 0. 0.')
M_inv = M

# GUI loop with image processing
while 1:

    # Capture a frame from video
    if devtype == 'SM5':
        buf = cap.getLastImage()

    frame = getImg(devtype, microscope, cv2cap=cap)

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
            cap.setExposure(exposure)

    if key & 0xFF == ord('-'):
        if devtype == 'SM5':
            exposure -= 1
            cap.setExposure(exposure)

    if key & 0xFF == ord('f'):
        try:
            _, _, _, frame = focus(devtype, microscope, template, cap)
            print 'Auto-focus done.'
        except TypeError:
            print 'Template image has not been taken yet.'

    if key & 0xFF == ord('b'):
        calibrate ^= 1
        calibrate_succeeded = 0
        template = 0
        step = 0

    if key & 0xFF == ord('p'):
        if calibrate_succeeded:
            pos = matrix('0.; 0.; 0.')
            pos[0, 0] = microscope.position(0) - init_pos_m[0]
            pos[1, 0] = microscope.position(1) - init_pos_m[1]
            if devtype == 'SM5':
                pos[2, 0] = microscope.position(2) - init_pos_m[2]
            else:
                pos[2, 0] = microscope.position(2) - init_pos_m[2]
            X = M_inv*pos
            for i in range(3):
                arm.absolute_move(init_pos_a[i]+alpha[i]*X[i], i)
        else:
            print 'Calibration must be done beforehand.'

    if key & 0xFF == ord('a'):
        microscope.relative_move(-100, 0)

    if calibrate:
        if step == 0:
            # Saving initial position of the arm and the microscope
            init_pos_a = [arm.position(0), arm.position(1), arm.position(2)]

            if devtype == 'SM5':
                init_pos_m = [microscope.position(0), microscope.position(1), microscope.position(2)]
            else:
                init_pos_m = [microscope.position(0), microscope.position(1), microscope.position(2)]

            # Get a series of template images for auto focus
            template = get_template_series(devtype, microscope, 5, cap)

            # Saving initial position of the tip on the screen
            _, _, loc = templatematching(frame, template[len(template)/2])
            x_init, y_init = loc[:2]

            # Getting the ratio um per pixels by moving the microscope by 100 um along x axis:

            # Moving the microscope
            microscope.relative_move(100, 0)
            cv2.waitKey(1000)

            # Refreshing the frame after the move
            frame = getImg(devtype, microscope, cv2cap=cap, update=1)
            cv2.imshow('Camera', frame)
            cv2.waitKey(1)

            # Getting the displacement, in pixels, of the tip on the screen
            _, _, loc = templatematching(frame, template[len(template)/2])
            dx = loc[0] - x_init
            dy = loc[1] - y_init

            # Determination of um_px
            um_px = 100./((dx**2 + dy**2)**0.5)

            # Resetting position of microscope
            microscope.relative_move(-100, 0)
            cv2.waitKey(1000)

            # Refreshing frame
            frame = getImg(devtype, microscope, cv2cap=cap, update=1)
            cv2.imshow('Camera', frame)
            cv2.waitKey(1)

            step += 1

            print 'Calibrated platform'

        elif step == 1:
            # calibrate arm x axis using exponential moves:
            # moves the arm, recenter the tip and refocus.
            # displacements are saved
            estim, frame = focus_track(devtype, microscope, arm, template, track_step, 0, alpha, um_px, estim, cap)
            cv2.imshow('Camera', frame)
            cv2.waitKey(1)
            print estim

            if nstep == maxnstep:

                # When the moves are finished:
                # Accuracy along z axis = total displacement +- 1um = 2**(maxnstep-1)-2 +-1

                # Update transformation matrix (Jacobian)
                M[0, 0] = alpha[0]*estim[0]
                M[1, 0] = alpha[1]*estim[1]
                M[2, 0] = alpha[2]*estim[2]

                # Resetting values used in calibration for the calibration of next axis
                estim = [0., 0., 0.]
                track_step = 2.
                nstep = 1

                # Resetting position of arm and microscope so no error gets to the next axis calibration
                for i in range(3):
                    arm.absolute_move(init_pos_a[i], i)
                    microscope.absolute_move(init_pos_m[i], i)

                cv2.waitKey(1000)

                # Update the frame
                frame = getImg(devtype, microscope, cv2cap=cap, update=1)
                cv2.imshow('Camera', frame)
                cv2.waitKey(10)

                step += 1
                print 'Calibrated x axis'

            else:
                nstep += 1
                track_step *= 2

        elif step == 2:
            # calibrate arm y axis
            estim, frame = focus_track(devtype, microscope, arm, template, track_step, 1, alpha, um_px, estim, cap)
            cv2.imshow('Camera', frame)
            cv2.waitKey(1)
            print estim

            if nstep == maxnstep:

                M[0, 1] = alpha[0]*estim[0]
                M[1, 1] = alpha[1]*estim[1]
                M[2, 1] = alpha[2]*estim[2]

                estim = [0., 0., 0.]
                nstep = 1
                track_step = 2.
                estloc = [0., 0.]

                for i in range(3):
                    arm.absolute_move(init_pos_a[i], i)
                    microscope.absolute_move(init_pos_m[i], i)

                cv2.waitKey(1000)

                frame = getImg(devtype, microscope, cv2cap=cap, update=1)
                cv2.imshow('Camera', frame)
                cv2.waitKey(1000)

                step += 1

                print 'Calibrated y axis'

            else:
                nstep += 1
                track_step *= 2

        elif step == 3:
            # calibrate arm z axis
            estim, frame = focus_track(devtype, microscope, arm, template, track_step, 2, alpha, um_px, estim, cap)

            cv2.imshow('Camera', frame)
            cv2.waitKey(1)
            print estim

            if nstep == maxnstep:

                M[0, 2] = alpha[0]*estim[0]
                M[1, 2] = alpha[1]*estim[1]
                M[2, 2] = alpha[2]*estim[2]

                estim = [0., 0., 0.]
                nstep = 1
                track_step = 2.

                for i in range(3):
                    arm.absolute_move(init_pos_a[i], i)
                    microscope.absolute_move(init_pos_m[i], i)

                cv2.waitKey(1000)

                frame = getImg(devtype, microscope, cv2cap=cap, update=1)
                cv2.imshow('Camera', frame)
                cv2.waitKey(1)

                step += 1
                print 'Calibrated z axis'

            else:
                nstep += 1
                track_step *= 2

        elif step == 4:

            print M
            M_inv = inv(M)
            print M_inv
            calibrate = 0
            calibrate_succeeded = 1
            print 'Calibration finished'

    # Our operations on the frame come here

    # Display a rectangle where the template will be taken
    frame = disp_template_zone(frame)
    # TODO: reverse frame along x and y axis, carefull might also need to reverse template images

    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

# When everything done, release the capture
stop_device(devtype, dev, microscope, cap)
