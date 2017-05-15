"""
Camera GUI for LuigsNeumann_SM10 and SM5
Requires OpenCV
To use autofocus, the user shall put the tip on focus in the displayed rectangle and press 't'
Autofocus using template matching by pressing 'f'
Display a rectangle around the detected tip
Quit with key 'q'
"""

from autofocus import *

# Type of used controller, either 'SM5' or 'SM10 for L&N SM-5 or L&N SM-10
devtype = 'SM10'

# Initializing the device, camera and microscope according to the used controller
dev, microscope, cap = init_device(devtype)

# Device controlling the used arm
arm = XYZUnit(dev, [1, 2, 3])

# Naming the live camera window
cv2.namedWindow('Camera')

# Booleans for tracking mode and existence of the template image for autofocus
track = 0
template = 0

# Step displacement for tracking an nuber of steps to make
step = 4
nsteps = 10

# GUI loop with image processing
while(True):

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
            maxval, _, _ = focus(devtype, microscope, template, cap, 4)
            print maxval
            print 'Autofocus done.'
        except TypeError:
            print 'Template image has not been taken yet.'

    if key & 0xFF == ord('t'):
        if type(template) == int:
            #template = img[height / 2 - 20:height / 2 + 20, width / 2 - 20:width / 2 + 20]
            template = get_template(img)
            cv2.imshow('template', template)
        else:
            template = 0
            cv2.destroyWindow('template')

    if key & 0xFF == ord('d'):
        track ^= 1

    # Tracking while moving
    if track != 0:
        arm.relative_move(step, 0)
        maxval, _, _ = focus(devtype, microscope, template, cap, 4)
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
        res, maxval, maxloc = templatematching(img, template)
        #print maxval
        if res:
            x, y = maxloc[:2]
            cv2.rectangle(frame, (x, y), (x + template.shape[1], y + template.shape[0]), (0, 255, 0))

    # Reversing the frame, FIND SOMETHING SO IT WORKS WITH TEMPLATE (REVERSE TEMPLATE ?)
    #frame = cv2.flip(frame, 2)

    # Display the resulting frame
    cv2.imshow('Camera', frame)

# When everything done, release the capture
stop_device(devtype, dev, microscope, cap)
