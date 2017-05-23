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
devtype = 'SM10'

# Initializing the device, camera and microscope according to the used controller
dev, microscope, cap = init_device(devtype)

# Device controlling the used arm and platform
arm = XYZUnit(dev, [1, 2, 3])
platform = XYZUnit(dev, [7, 8, 9])

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

# Initial estimation (displacement z_microscope)/(displ moved axis), in um/um
estim = 0.

# Initial estimation (displacement x:y_microscope)/(displ moved axis), in um/um
estloc = [0., 0.]

# Orientation
alpha = [1., -1., 1.]

# Initializing transformation matrix (Jacobian)
M = matrix('0. 0. 0.; 0. 0. 0.; 0. 0. 0.')

# GUI loop with image processing
while 1:

    # Capture a frame from video
    if devtype == 'SM5':
        buf = microscope.getLastImage()

    frame = getImg(devtype, microscope, cv2cap=cap)

    # Keyboards controls:
    # 'q' to quit,
    # 'f' for autofocus,
    # 'b' to begin calibration
    # 'p' to center the tip, after calibration
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

    if key & 0xFF == ord('f'):
        try:
            _, _, _, frame = focus(devtype, microscope, template, cap)
            print 'Autofocus done.'
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
                pos[2, 0] = microscope.getPosition() - init_pos_m[2]
            else:
                pos[2, 0] = microscope.position(2) - init_pos_m[2]
            X = M_inv*pos
            arm.absolute_move_group([init_pos_a[0]+alpha[0]*X[0], init_pos_a[1]+alpha[1]*X[1], init_pos_a[2]+alpha[2]*X[2]], [0, 1, 2])
        else:
            print 'Calibration must be done beforehand.'

    if calibrate:
        if step == 0:
            # Saving initial position of the arm and the platform/microscope
            init_pos_a = [arm.position(0), arm.position(1), arm.position(2)]

            if devtype == 'SM5':
                init_pos_m = [platform.position(0), platform.position(1), microscope.getPosition()]
            else:
                init_pos_m = [platform.position(0), platform.position(1), platform.position(2)]

            # Get a series of template images for auto focus
            template = get_template_series(devtype, microscope, 5, cap)

            # Saving initial position of the tip on the screen
            _, _, loc = templatematching(frame, template[len(template)/2])
            x_init, y_init = loc[:2]

            # Getting the ratio um per pixels by moving the platform by 100 um along x axis:

            # Moving the platform
            platform.relative_move(100, 0)

            # Refreshing the frame after the move
            frame = getImg(devtype, microscope, cv2cap=cap, update=1)
            cv2.imshow('Camera', frame)
            cv2.waitKey(1)

            # Getting the displacement, in pixels, of the tip on the screen
            _, _, loc = templatematching(frame, template[len(template)/2])
            dx = loc[0] - x_init
            dy = loc[1] - y_init

            # Determination of um_px should be done with a move of the platform greater than the (total) ones of the arm
            # Thus the calibration would be accurate
            um_px = 100./((dx**2 + dy**2)**0.5)

            # Resetting position of platform
            platform.relative_move(-100, 0)

            # Refreshing frame
            frame = getImg(devtype, microscope, cv2cap=cap, update=1)
            cv2.imshow('Camera', frame)
            cv2.waitKey(1)

            step += 1

            print 'step 0 done'

        elif step == 1:
            # calibrate arm x axis using exponential moves:
            # moves the arm, recenter the tip and refocus.
            # displacements are saved
            estim, estloc, frame = focus_track(devtype, microscope, arm, template, track_step, 0, alpha, um_px, estim, estloc, cap)
            cv2.imshow('Camera', frame)
            cv2.waitKey(1)

            if nstep == maxnstep:

                # When the moves are finished:
                # Accuracy along axis = total displacement +- 1um = 2**(maxnstep-1)-2 +-1

                # Depack calibration along axis x and y of the platform
                x, y = estloc[:2]

                # Update transformation matrix (Jacobian)
                M[0, 0] = x
                M[1, 0] = -y
                M[2, 0] = estim

                # Resetting values used in calibration for the calibration of next axis
                estim = 0
                track_step = 2.
                nstep = 1
                estloc = [0., 0.]

                # Resetting position of arm and platform so no error gets to the next axis calibration
                arm.absolute_move_group(init_pos_a, [0, 1, 2])
                microscope.absolute_move_group(init_pos_m, [0, 1, 2])

                # Update the frame
                frame = getImg(devtype, microscope, cv2cap=cap, update=1)
                cv2.imshow('Camera', frame)
                cv2.waitKey(10)

                step += 1
                print 'step 1 done'

            else:
                nstep += 1
                track_step *= 2

        elif step == 2:
            # calibrate arm y axis
            estim, estloc, frame = focus_track(devtype, microscope, arm, template, track_step, 1, alpha, um_px, estim, estloc, cap)
            cv2.imshow('Camera', frame)
            cv2.waitKey(1)

            if nstep == maxnstep:

                x, y = estloc[:2]

                M[0, 1] = x
                M[1, 1] = -y

                M[2, 1] = estim

                estim = 0
                nstep = 1
                track_step = 2.
                estloc = [0., 0.]

                arm.absolute_move_group(init_pos_a, [0, 1, 2])
                microscope.absolute_move_group(init_pos_m, [0, 1, 2])
                frame = getImg(devtype, microscope, cv2cap=cap, update=1)
                cv2.imshow('Camera', frame)
                cv2.waitKey(1000)

                step += 1

                print 'step 2 done'

            else:
                nstep += 1
                track_step *= 2

        elif step == 3:
            # calibrate arm z axis
            estim, estloc, frame = focus_track(devtype, microscope, arm, template, track_step, 2, alpha, um_px, estim, estloc, cap)

            cv2.imshow('Camera', frame)
            cv2.waitKey(1)

            if nstep == maxnstep:

                x, y = estloc[:2]

                M[0, 2] = x
                M[1, 2] = -y
                M[2, 2] = estim

                estim = 0
                nstep = 1
                track_step = 2.
                estloc = [0., 0.]

                arm.absolute_move_group(init_pos_a, [0, 1, 2])
                microscope.absolute_move_group(init_pos_m, [0, 1, 2])

                frame = getImg(devtype, microscope, cv2cap=cap, update=1)
                cv2.imshow('Camera', frame)
                cv2.waitKey(1)

                step += 1
                print 'step 3 done'

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
    #if type(template) == int:
    # Display a rectangle where the template will be taken
    frame = disp_template_zone(frame)
    #else:
        # Display a rectangle at the template matched location
        #res, maxval, maxloc = templatematching(frame, template[len(template)/2])
        #if res:
            #x, y = maxloc[:2]
            #cv2.rectangle(frame, (x, y), (x + template[len(template)/2].shape[1], y + template[len(template)/2].shape[0]), (0, 255, 0))

    # Reversing the frame, FIND SOMETHING SO IT WORKS WITH TEMPLATE (REVERSE TEMPLATE ?)
    #frame = cv2.flip(frame, 2)

    # Display the resulting frame
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

# When everything done, release the capture
stop_device(devtype, dev, microscope, cap)
