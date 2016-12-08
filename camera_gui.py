'''
Camera window.
Requires Opencv.
'''
import numpy as np
import cv2

cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    width, height, _ = frame.shape

    # Our operations on the frame come here
    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cv2.line(frame, (height/2, width/2-10), (height/2, width/2+10), (0, 0, 255))
    cv2.line(frame, (height/2-10, width/2), (height/2+10, width/2), (0, 0, 255))

    #print frame

    # Display the resulting frame
    cv2.imshow('Camera',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
