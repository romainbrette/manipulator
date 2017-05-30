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
devtype = 'SM5'

# Initializing the device, camera and microscope according to the used controller
dev, microscope, arm, cap = init_device(devtype, 'dev1')

# Exposure for the camera when using MicroManager
exposure = 15

# Naming the live camera window
cv2.namedWindow('Camera', flags=cv2.WINDOW_NORMAL)

# Booleans for tracking mode and existence of the template image for autofocus
track = 0
template = 0

# Step displacement for tracking an nuber of steps to make
step = 4
nsteps = 10

M = matrix([[8.94138912e-01,   4.79193908e-02,  -6.26874856e-03],
 [ -3.50742251e-02,   1.00653796e+00,   2.01907546e-03],
 [ -4.64880720e-01,  -7.16744866e-05,   1.01580666e+00]])
M_inv = inv(M)

alpha = matrix([[-0.99343753, -0.1209118 ],
 [ 0.11437603, -0.9999733 ]])

# GUI loop with image processing
while(True):

    # Capture a frame from video
    buffer = cap.getLastImage()

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
            #maxval, _, _, frame = focus(devtype, microscope, template, cap, 4)
            print maxval
            print 'Autofocus done.'
        except TypeError:
            print 'Template image has not been taken yet.'

    if key & 0xFF == ord('t'):
        if type(template) == int:
            init_pos_a = [arm.position(i) for i in range(3)]
            init_pos_m = [microscope.position(i) for i in range(3)]
            #template = frame[height / 2 - 20:height / 2 + 20, width / 2 - 20:width / 2 + 20]
            #template = get_template(frame)
            #cv2.imshow('template', template)
        else:
            template = 0
            #cv2.destroyWindow('template')

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
        for i in range(3):
            pos[i, 0] =  microscope.position(i) - init_pos_m[i]

        X = M_inv * pos
        for i in range(3):
            arm.absolute_move(init_pos_a[i] + X[i], i)


    # Tracking while moving
    if track != 0:
        arm.relative_move(step, 0)
        maxval, _, _, frame = dfocus(devtype, microscope, template, cap, step)
        track += 1
    if track == nsteps:
        track = 0
        print 'Tracking finished'

    # Our operations on the frame come here
    if not isinstance(template, list):
        # Display a rectangle where the template will be taken
        frame = disp_template_zone(frame)

    # Display a red centered cross
    frame = disp_centered_cross(frame)

    # Reversing the frame, FIND SOMETHING SO IT WORKS WITH TEMPLATE (REVERSE TEMPLATE ?)
    #frame = cv2.flip(frame, 2)

    # Display the resulting frame
    cv2.imshow('Camera', frame)

# When everything done, release the capture
stop_device(devtype, dev, microscope, cap)
