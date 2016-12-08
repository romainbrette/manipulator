'''
Camera window.
Requires Opencv.

Note: my infinity camera has variable resolution, but
it seems that OpenCV sets it to 640x480 by default (maybe could be set)
'''
import numpy as np
import cv2

def click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print x,y

cap = cv2.VideoCapture(0)
cv2.namedWindow('Camera')
cv2.setMouseCallback("Camera", click)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    width, height, _ = frame.shape

    # Our operations on the frame come here
    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cv2.line(frame, (height/2, width/2-10), (height/2, width/2+10), (0, 0, 255))
    cv2.line(frame, (height/2-10, width/2), (height/2+10, width/2), (0, 0, 255))

    # Display the resulting frame
    cv2.imshow('Camera',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
