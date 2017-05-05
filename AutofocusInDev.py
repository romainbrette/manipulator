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

# Devices to control
try:
    dev = LuigsNeumann_SM10()
except SerialException:
    print "L&N SM-10 not found. Falling back on fake device."
    dev = FakeDevice()

microscope = XYZUnit(dev, [7, 8, 9])
arm = XYZUnit(dev, [1, 2, 3])

track = 0

# GUI loop with image processing
while(True):

    # keyboards controls: 'q' to quit, 'f' for autofocus
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

    if key & 0xFF == ord('f'):
        tipfocus(microscope, cap)
        print 'Autofocus done.'

    if key & 0xFF == ord('d'):
        track ^= 1

    if track != 0:
        arm.relative_move(2, 0)
        tipfocus(microscope, cap)
        track += 1
    if track == 10:
        track = 0

    # Capture a frame from video with usable image for tipdetect()
    frame, img = getImg(cap)

    # Detection of the tip
    x, y, c = tip_detect(img)

    # Display a rectangle around the detected tip
    #cv2.rectangle(frame, (x-10, y-10), (x+10, y+10), (0, 0, 255))

    # Our operations on the frame come here
    frame = cv2.flip(frame, 2)

    # Display the resulting frame
    cv2.imshow('Camera', frame)

    # Debugging
    #print str((1e4*c)**5)+', '+str(microscope.position(2))+', '


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
del dev
