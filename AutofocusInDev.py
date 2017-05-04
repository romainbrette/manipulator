'''
Autofocusing the tip of the pipette.
Use the tip_detection function
Show the camera window for debugging.
Requires Opencv.
Quit with key 'q'
'''
import cv2
from autofocus import *
from devices import *
from serial import SerialException

cap = cv2.VideoCapture(0)

#width = int(cap.get(3))
#height = int(cap.get(4))

cv2.namedWindow('Camera')

focus = 0

try:
    dev = LuigsNeumann_SM10()
except SerialException:
    print "L&N SM-10 not found. Falling back on fake device."
    dev = FakeDevice()

microscope = XYZUnit(dev, [7, 8, 9])

while(True):

    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

    if key & 0xFF == ord('f'):
        focus ^= 1

    frame, img = getImg(cap)

    # Detection of the tip, frame has to be encoded to an usable image
    x, y, c = tip_detect(img)
    print c
    if focus == 1:
        tipfocus(microscope, cap)

    # Display a circle around the detected tip

    cv2.rectangle(frame, (x-10, y-10), (x+10, y+10), (0, 0, 255))

    # Our operations on the frame come here

    frame = cv2.flip(frame, 2)

    # Display the resulting frame
    cv2.imshow('Camera', frame)



# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
del dev
