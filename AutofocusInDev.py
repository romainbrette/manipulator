'''
Autofocusing the tip of the pipette.
Use the tip_detection function
Show the camera window for debugging.
Requires Opencv.
Quit with key 'q'
'''
import cv2
from vision import *

cap = cv2.VideoCapture(0)

width = int(cap.get(3))
height = int(cap.get(4))

cv2.namedWindow('Camera')

while(True):

    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

    # Capture frame-by-frame
    ret, frame = cap.read()

    # Detection of the tip, frame has to be encoded to an usable image
    retval, img = cv2.imencode('.jpg', frame)
    x, y, c = tip_detection(cv2.imdecode(img, 0))
    print c

    # Display a circle around the detected tip

    cv2.rectangle(frame, (x-10, y-10), (x+10, y+10), (0, 0, 255))

    # Our operations on the frame come here

    frame = cv2.flip(frame, 1)

    # Display the resulting frame
    cv2.imshow('Camera', frame)



# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
