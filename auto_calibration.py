"""
Camera GUI for LuigsNeumann_SM10 and SM5
Requires OpenCV
To use autofocus, the user shall put the tip on focus in the displayed rectangle and press 't'
Autofocus using template matching by pressing 'f'
Display a rectangle around the detected tip
Quit with key 'q'
"""

from autofocus import *
from numpy import matrix
from numpy.linalg import inv

# Type of used controller, either 'SM5' or 'SM10 for L&N SM-5 or L&N SM-10
devtype = 'SM10'

# Initializing the device, camera and microscope according to the used controller
dev, microscope, cap = init_device(devtype)

# Device controlling the used arm
arm = XYZUnit(dev, [1, 2, 3])
platform = XYZUnit(dev, [7, 8, 9])

# Naming the live camera window
cv2.namedWindow('Camera', flags=cv2.WINDOW_NORMAL)

# Booleans for tracking mode and existence of the template image for autofocus
template = 0
calibrate = 0
calibrate_succeded = 0
step = 0
nstep = 1
maxnstep = 5
track_step = 2
estim = 0.
estloc = [0.,0.]
alpha = [1., -1., 1.]
M = matrix('0. 0. 0.; 0. 0. 0.,; 0. 0. 0.')

# GUI loop with image processing
while 1:

    # Capture a frame from video
    if devtype == 'SM5':
        buffer = microscope.getLastImage()

    frame, img, cap = getImg(devtype, microscope, cv2cap=cap)

    # Keyboards controls:
    # 'q' to quit,
    # 'f' for autofocus,
    # 't' to take the template image,
    # 'd' to make/stop a move with focus tracking
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

    if key & 0xFF == ord('f'):
        try:
            maxval, _, _, frame, cap = focus(devtype, microscope, template, cap, 10)
            print maxval
            print 'Autofocus done.'
        except TypeError:
            print 'Template image has not been taken yet.'

    if key & 0xFF == ord('b'):
        calibrate ^= 1
        calibrate_succeded = 0
        template = 0
        step = 0

    if key & 0xFF == ord('p'):
        if calibrate_succeded:
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

            init_pos_a = [arm.position(0), arm.position(1), arm.position(2)]

            if devtype == 'SM5':
                init_pos_m = [platform.position(0), platform.position(1), microscope.getPosition()]
            else:
                init_pos_m = [platform.position(0), platform.position(1), platform.position(2)]

            template = get_template(img)
            cv2.imshow('template', template)

            _, _, loc = templatematching(img, template)
            x_init, y_init = loc[:2]

            platform.relative_move(100, 0)
            frame, img, cap = getImg(devtype, microscope, init_pos_m[2], cv2cap=cap)

            cv2.imshow('Camera', frame)
            cv2.waitKey(1)

            step += 1

        elif step == 1:

            _, _, loc = templatematching(img, template)
            dx = loc[0] - x_init
            dy = loc[1] - y_init
            # Determination of um_px should be done with a move of the platform greater than the (total) ones of the arm
            # Thus the calibration would be accurate
            um_px = 100./((dx**2 + dy**2)**0.5)

            platform.relative_move(-100, 0)

            frame, img, cap = getImg(devtype, microscope, init_pos_m[2], cv2cap=cap)

            cv2.imshow('Camera', frame)
            cv2.waitKey(1)

            step += 1

            print 'step 0 done'

        elif step == 2:

            # calibrate arm x axis
            estim, estloc, frame, cap = focus_track(devtype, microscope, arm, template, track_step, 0, alpha, um_px, estim, estloc, cap)
            frame, img, cap = getImg(devtype, microscope, cv2cap=cap)
            cv2.imshow('Camera', frame)
            cv2.waitKey(1)
            if nstep == maxnstep:
                x, y = estloc[:2]
                #M[0, 0] = (x - x_init)*um_px/(2**(maxnstep+1)-2)
                #M[1, 0] = (y - y_init)*um_px/(2**(maxnstep+1)-2)
                M[0, 0] = x
                M[1, 0] = y
                M[2, 0] = estim

                estim = 0
                track_step = 2
                nstep = 1
                estloc = [0.,0.]
                #x_init = x
                #y_init = y
                frame, img, cap = getImg(devtype, microscope, cv2cap=cap)
                cv2.imshow('Camera', frame)
                cv2.waitKey(1)

                step += 1
                print 'step 1 done'
            else:
                nstep += 1
                track_step *= 2
        elif step == 3:
            # calibrate arm y axis
            estim, estloc, frame, cap = focus_track(devtype, microscope, arm, template, track_step, 1, alpha, um_px, estim, estloc, cap)
            frame, img, cap = getImg(devtype, microscope, cv2cap=cap)
            cv2.imshow('Camera', frame)
            cv2.waitKey(1)
            #arm.relative_move(track_step, 1)
            #_, _, loc = templatematching(img, template)
            if nstep == maxnstep:

                x, y = loc[:2]
                #M[0, 1] = (x - x_init)*um_px/(2**(maxnstep+1)-2)
                #M[1, 1] = (y - y_init)*um_px/(2**(maxnstep+1)-2)
                M[0, 1] = x
                M[1, 1] = y

                M[2, 1] = estim

                estim = 0
                nstep = 1
                track_step = 2
                estloc = [0., 0.]
                #x_init = x
                #y_init = y
                frame, img, cap = getImg(devtype, microscope, cv2cap=cap)
                cv2.imshow('Camera', frame)
                cv2.waitKey(1)

                step += 1
                print 'step 2 done'

            else:
                nstep += 1
                track_step *= 2

        elif step == 4:
            # calibrate arm z axis
            estim, estloc, frame, cap = focus_track(devtype, microscope, arm, template, track_step, 2, alpha, um_px, estim, estloc, cap)
            frame, img, cap = getImg(devtype, microscope, cv2cap=cap)
            cv2.imshow('Camera', frame)
            cv2.waitKey(1)
            if nstep == maxnstep:

                x, y = estloc[:2]
                #M[0, 2] = (x - x_init)*um_px/(2**(maxnstep+1)-2)
                #M[1, 2] = (y - y_init)*um_px/(2**(maxnstep+1)-2)
                M[0, 2] = x
                M[1, 2] = y
                M[2, 2] = estim

                estim = 0
                nstep = 1
                track_step = 2
                estloc = [0., 0.]
                frame, img, cap = getImg(devtype, microscope, cv2cap=cap)
                cv2.imshow('Camera', frame)
                cv2.waitKey(1)

                step += 1
                print 'step 3 done'

            else:
                nstep += 1
                track_step *= 2

        elif step == 5:
            print M
            M_inv = inv(M)
            print M_inv
            calibrate = 0
            calibrate_succeded = 1
            print 'Calibration finished'

    # Our operations on the frame come here
    if type(template) == int:
        # Display a rectangle where the template will be taken
        frame = disp_template_zone(frame)
    else:
        # Display a rectangle at the template matched location
        res, maxval, maxloc = templatematching(img, template)
        # print maxval
        if res:
            x, y = maxloc[:2]
            cv2.rectangle(frame, (x, y), (x + template.shape[1], y + template.shape[0]), (0, 255, 0))

    # Reversing the frame, FIND SOMETHING SO IT WORKS WITH TEMPLATE (REVERSE TEMPLATE ?)
    #frame = cv2.flip(frame, 2)

    # Display the resulting frame
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

# When everything done, release the capture
stop_device(devtype, dev, microscope, cap)
