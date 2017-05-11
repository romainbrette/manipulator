"""
Camera GUI for LuigsNeumann_SM10 and SM5
Requires OpenCV
To use autofocus, the user shall put the tip on focus in the displayed rectangle and press 't'
Autofocus using template matching by pressing 'f'
Display a rectangle around the detected tip
Quit with key 'q'
"""

import cv2
from devices import *
from serial import SerialException
from autofocus import *

# Devices to control and video capture

# Type of used controller, either 'SM5' or 'SM10 for L&N SM-5 or L&N SM-10
devtype = 'SM10'

# Initializing the device, camera and microscope according to the used controller
if devtype == 'SM5':
    try:
        dev = LuigsNeumann_SM5('COM3')
        cap = None
        microscope = camera_init()
        microscope.startContinuousSequenceAcquisition(1)
    except Warning:
        raise SerialException("L&N SM-5 not found.")
elif devtype == 'SM10':
    try:
        dev = LuigsNeumann_SM10()
        cap = cv2.VideoCapture(0)
        microscope = XYZUnit(dev, [7, 8, 9])
    except SerialException:
        raise SerialException("L&N SM-10 not found.")
else:
    raise SerialException("No supported device detected")

# Device controlling the used arm
arm = XYZUnit(dev, [1, 2, 3])

# Naming the live camera window
cv2.namedWindow('Camera')

# Booleans for tracking mode and existence of the template image for autofocus
track = 0
template = None

# GUI loop with image processing
while(True):

    # Capture a frame from video
    if devtype == 'SM5':
        buffer = microscope.getLastImage()
        height, width = buffer.shape[:2]

    frame, img = getImg(devtype, microscope, cv2cap=cap)

    if devtype == 'SM10':
        height, width = frame.shape[:2]

    ##img = cv2.Canny(img, 50, 200)

    # Detection of the tip
    #x, y, c = tip_detect(img)

    # Display a rectangle around the detected tip
    #cv2.rectangle(frame, (x-10, y-10), (x+10, y+10), (0, 0, 255))

    # Keyboards controls:
    # 'q' to quit,
    # 'f' for autofocus,
    # 't' to take the template image,
    # 'd' to make/stop a move with focus tracking
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

    if key & 0xFF == ord('f'):
        #tipfocus(microscope, cap)
        maxval, x, y = focus(devtype, microscope, template, cap)
        print maxval
        print 'Autofocus done.'

    if key & 0xFF == ord('t'):
        if template == None:
            template = img[height / 2 - 20:height / 2 + 20, width / 2 - 20:width / 2 + 20]
            ##template = cv2.Canny(template, 50, 200)
            xtip, ytip, _ = tip_detect(template)
            cv2.rectangle(template, (xtip-10, ytip-10), (xtip+10, ytip+10), (0, 0, 255))
            cv2.imshow('template', template)
        else:
            template = None

    if key & 0xFF == ord('d'):
        track ^= 1

    # Tracking while moving
    if track != 0:
        arm.relative_move(-2, 0)
        #tipfocus(microscope, cap)
        maxval, x, y = focus(devtype, microscope, template, cap)
        track += 1
    if track == 10:
        track = 0
        print 'Tracking finished'

    # Our operations on the frame come here
    if template == None:
        # Display a rectangle where the template will be taken
        cv2.rectangle(frame, (width/2-20, height/2-20), (width/2+20, height/2+20), (0,0,255))
    else:
        # Display a rectangle at the template matched location
        res, maxval, maxloc = templatematching(getImg(devtype, microscope, cv2cap=cap)[1], template)
        #print maxval
        if res:
            x, y = maxloc[:2]
            cv2.rectangle(frame, (x, y), (x + 20, y + 20), (0, 0, 255))

    # Reversing the frame
    frame = cv2.flip(frame, 2)

    # Display the resulting frame
    cv2.imshow('Camera', frame)

    # Debugging
    #print str((1e4*c)**5)+', '+str(microscope.position(2))+', '


# When everything done, release the capture

if devtype == 'SM5':
    microscope.stopSequenceAcquisition()
    camera_unload(microscope)
    microscope.reset()
elif devtype == 'SM10':
    cap.release()

cv2.destroyAllWindows()
del dev
