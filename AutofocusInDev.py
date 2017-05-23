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
track = 0
template = 0

# Step displacement for tracking an nuber of steps to make
step = 4
nsteps = 10

M = matrix([[0.80672554,  0.05661232, -0.00566123],
        [0.0537817, -1.01052989, -0.],
        [-0.5546875,  0.,  1.]])

M_inv = inv(M)

alpha = [1., -1., 1.]

# GUI loop with image processing
while(True):

    # Capture a frame from video
    if devtype == 'SM5':
        buffer = microscope.getLastImage()

    frame = getImg(devtype, microscope, cv2cap=cap)

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
            maxval, _, _, frame = dfocus(devtype, microscope, template, cap, 4)
            print maxval
            print 'Autofocus done.'
        except TypeError:
            print 'Template image has not been taken yet.'

    if key & 0xFF == ord('t'):
        if type(template) == int:
            init_pos_a = [arm.position(0), arm.position(1), arm.position(2)]

            if devtype == 'SM5':
                init_pos_m = [platform.position(0), platform.position(1), microscope.getPosition()]
            else:
                init_pos_m = [platform.position(0), platform.position(1), platform.position(2)]
            #template = frame[height / 2 - 20:height / 2 + 20, width / 2 - 20:width / 2 + 20]
            template = get_template(frame)
            cv2.imshow('template', template)
        else:
            template = 0
            cv2.destroyWindow('template')

    if key & 0xFF == ord('d'):
        track ^= 1

    if key & 0xff == ord('g'):
        frame = getImg(devtype, microscope, cv2cap=cap)
        cv2.imshow('before', frame)
        cv2.waitKey(1)
        arm.relative_move(100, 0)
        frame = getImg(devtype, microscope, cv2cap=cap, update=1)
        cv2.imshow('after', frame)
        cv2.waitKey(1)

    if key & 0xFF == ord('p'):
        pos = matrix('0.; 0.; 0.')
        pos[0, 0] = microscope.position(0) - init_pos_m[0]
        pos[1, 0] = microscope.position(1) - init_pos_m[1]
        if devtype == 'SM5':
            pos[2, 0] = microscope.getPosition() - init_pos_m[2]
        else:
            pos[2, 0] = microscope.position(2) - init_pos_m[2]
        X = M_inv*pos
        arm.absolute_move_group([init_pos_a[0]+alpha[0]*X[0], init_pos_a[1]+alpha[1]*X[1], init_pos_a[2]+alpha[2]*X[2]], [0, 1, 2])


    # Tracking while moving
    if track != 0:
        arm.relative_move(step, 0)
        maxval, _, _, frame = dfocus(devtype, microscope, template, cap, step)
        track += 1
    if track == nsteps:
        track = 0
        print 'Tracking finished'

    # Our operations on the frame come here
    if type(template) == int:
        # Display a rectangle where the template will be taken
        frame = disp_template_zone(frame)
    else:
        # Display a rectangle at the template matched location
        res, maxval, maxloc = templatematching(frame, template)
        print maxval
        if res:
            x, y = maxloc[:2]
            cv2.rectangle(frame, (x, y), (x + template.shape[1], y + template.shape[0]), (0, 255, 0))

    # Reversing the frame, FIND SOMETHING SO IT WORKS WITH TEMPLATE (REVERSE TEMPLATE ?)
    #frame = cv2.flip(frame, 2)

    # Display the resulting frame
    cv2.imshow('Camera', frame)

# When everything done, release the capture
stop_device(devtype, dev, microscope, cap)
