"""
Camera GUI
Requires OpenCV
Display a rectangle around the detected tip
Press 'f' to focus on the tip
Quit with key 'q'
"""

import cv2
from autofocus import *
from devices import *
from serial import SerialException

# Capture Video input
cap = cv2.VideoCapture(0)
cv2.namedWindow('Camera')
width, height = cap.frame[:2]

# Devices to control
try:
    dev = LuigsNeumann_SM10()
except SerialException:
    print "L&N SM-10 not found. Falling back on fake device."
    dev = FakeDevice()

microscope = XYZUnit(dev, [7, 8, 9])
arm = XYZUnit(dev, [1, 2, 3])

track = 0
template = None

# GUI loop with image processing
while(True):

    # Capture a frame from video with usable image for tipdetect()
    frame, img = getImg(cap)
    ##img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ##img = cv2.Canny(img, 50, 200)

    # Detection of the tip
    #x, y, c = tip_detect(img)

    # Display a rectangle around the detected tip
    #cv2.rectangle(frame, (x-10, y-10), (x+10, y+10), (0, 0, 255))

    # keyboards controls:
    # 'q' to quit,
    # 'f' for autofocus,
    # 't' to take the template image,
    # 'd' to make a move with focus tracking
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

    if key & 0xFF == ord('f'):
        #tipfocus(microscope, cap)
        maxval, x, y = focus(cap, template, microscope)
        print 'Autofocus done.'

    if key & 0xFF == ord('t'):
        template = img[width / 2 - 10:width / 2 + 10, height / 2 - 10:height / 2 + 10]
        ##template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        ##template = cv2.Canny(template, 50, 200)
        cv2.imshow('template', template)

    if key & 0xFF == ord('d'):
        track ^= 1

    if track != 0:
        arm.relative_move(2, 0)
        #tipfocus(microscope, cap)
        maxval, x, y = focus(cap, template, microscope)
        track += 1
    if track == 10:
        track = 0
        print 'Tracking finished'

    # Our operations on the frame come here
    if template == None:
        # Display a rectangle where the template will be taken
        cv2.rectangle(frame, (width/2-10, height/2-10), (width/2+10, height/2+10), (0,0,255))
    else:
        # Display a rectangle at the template matched location
        cv2.rectangle(frame, (x,y), (x+20,y+20), (0,0,255))

    frame = cv2.flip(frame, 2)

    # Display the resulting frame
    cv2.imshow('Camera', frame)

    # Debugging
    #print str((1e4*c)**5)+', '+str(microscope.position(2))+', '


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
del dev
