'''
Detect movement in Paramecium video (x20)
'''
import cv2
from time import sleep

#filename = '/Users/Romain/ownCloud/Paramecium/Comportement/Videos au 20x/gouttelette2.mp4'
filename = '/Users/Romain/Desktop/paramecie 1.mov'

cap = cv2.VideoCapture(filename)
#cap = cv2.VideoCapture(0)

firstFrame = None

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret:

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        if firstFrame is None:
            firstFrame = gray
            continue

        # compute the absolute difference between the current frame and
        # first frame
        frameDelta = cv2.absdiff(firstFrame, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                     cv2.CHAIN_APPROX_SIMPLE)

        # loop over the contours
        for i,c in enumerate(cnts):
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < 10000:
                continue

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.drawContours(frame, cnts, i, (0, 255, 0), 3)

            # Calculate moments / From this one could get the orientation
            M = cv2.moments(c)
            cx = M['m10']/M['m00']
            cy = M['m01']/M['m00']

            cv2.rectangle(frame, (int(cx)-2,int(cy)-2), (int(cx)+2,int(cy)+2), (0, 255, 0), 2)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        #sleep(0.1)

cap.release()
cv2.destroyAllWindows()
