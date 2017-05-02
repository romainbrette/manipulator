'''
Camera window.
Requires Opencv.
Quit with key 'q'

Note: my infinity camera has variable resolution, but
it seems that OpenCV sets it to 640x480 by default (maybe could be set)
'''
import cv2

cap = cv2.VideoCapture(0)

width = int(cap.get(3))
height = int(cap.get(4))

cv2.namedWindow('Camera')


while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here

    frame = cv2.flip(frame, 1)

    # Display the resulting frame
    cv2.imshow('Camera',frame)

    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
