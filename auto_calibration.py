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
cv2.namedWindow('Camera')

# Booleans for tracking mode and existence of the template image for autofocus
template = 0
calibrate = 0
step = 0
track_step = 1
estim = 0
M = matrix('0 0 0; 0 0 0,; 0 0 0')

# GUI loop with image processing
while 1:

    # Capture a frame from video
    if devtype == 'SM5':
        buffer = microscope.getLastImage()

    frame, img = getImg(devtype, microscope, cv2cap=cap)

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
            maxval, _ = focus(devtype, microscope, template, cap, 10)
            print maxval
            print 'Autofocus done.'
        except TypeError:
            print 'Template image has not been taken yet.'

    if key & 0xFF == ord('b'):
        calibrate ^= 1

    if calibrate:
        if step == 0:
            #template = img[height / 2 - 20:height / 2 + 20, width / 2 - 20:width / 2 + 20]
            init_pos_a = [arm.position(0), arm.position(1), arm.position(2)]
            if devtype == 'SM5':
                init_pos_m = [platform.position(0), platform.position(1), microscope.getPosition]
            else:
                init_pos_m = [platform.position(0), platform.position(1), platform.position(2)]
            template = get_template(img)
            cv2.imshow('template', template)
            _, _, loc = templatematching(img, template)
            x_init, y_init = loc[:2]
            platform.relative_move(50, 0)
            _, img = getImg(devtype, microscope, cv2cap=cap)
            _, _, loc = templatematching(img, template)
            dy = loc[1] - y_init
            um_px = 50./dy
            platform.relative_move(-50, 0)
            step += 1
        elif step == 1:
            # calibrate arm x axis
            estim, loc = focus_track(devtype, microscope, arm, track_step, 0, estim, cap)
            track_step *= 2
            if track_step == 32:
                x, y = loc[:2]
                M[0, 0] = x*um_px
                M[1, 0] = y*um_px
                M[2, 0] = estim
                estim = 0
                track_step = 1
                arm.absolute_move(init_pos_a[0], 0)
                _, _ = getImg(devtype, microscope, init_pos_m[2], cap)
                step += 1
        elif step == 2:
            # calibrate arm y axis
            estim, loc = focus_track(devtype, microscope, arm, track_step, 1, estim, cap)
            track_step *= 2
            if track_step == 32:
                x, y = loc[:2]
                M[0, 1] = x*um_px
                M[1, 1] = y*um_px
                M[2, 1] = estim
                estim = 0
                track_step = 1
                arm.absolute_move(init_pos_a[1], 1)
                _, _ = getImg(devtype, microscope, init_pos_m[2], cap)
                step += 1
        elif step == 3:
            # calibrate arm z axis
            estim, loc = focus_track(devtype, microscope, arm, track_step, 2, estim, cap)
            track_step *= 2
            if track_step == 32:
                x, y = loc[:2]
                M[0, 2] = x*um_px
                M[1, 2] = y*um_px
                M[2, 2] = estim
                estim = 0
                track_step = 1
                arm.absolute_move(init_pos_a[2], 2)
                _, _ = getImg(devtype, microscope, init_pos_m[2], cap)
                step += 1
        elif step == 4:
            M_inv = inv(M)
            calibrate = 0
            print 'Calibration finished'
            pass

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
            cv2.rectangle(frame, (x, y), (x + template.shape[0], y + template.shape[1]), (0, 255, 0))

    # Reversing the frame, FIND SOMETHING SO IT WORKS WITH TEMPLATE (REVERSE TEMPLATE ?)
    #frame = cv2.flip(frame, 2)

    # Display the resulting frame
    cv2.imshow('Camera', frame)

# When everything done, release the capture
stop_device(devtype, dev, microscope, cap)
