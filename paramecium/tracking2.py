'''
Tracking based on Eric Furst's paper.
'''
from pylab import *
import pims
import cv2
from time import sleep

filename = '/Users/Romain/Desktop/paramecie 1.mov'

cap = cv2.VideoCapture(filename)

previous = None

#frames = pims.Video(filename)
#frame = frames[0]#[:,:,0] # convert to gray
#frame = frame*1.

noise_length = 51
cell_length = 301

while(True):
    _, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if (previous is None):
        previous = gray
        continue

    # compute the absolute difference between the current frame and
    # first frame
    #frameDelta = cv2.absdiff(previous, gray)
    #thresh = cv2.threshold(frameDelta, 10, 255, cv2.THRESH_BINARY)[1]

    norm_image = -cv2.normalize(gray, alpha = 255, beta = 0, norm_type = cv2.NORM_MINMAX)
    #norm_image = cv2.dilate(norm_image, None, iterations=2)
    #norm_image = gray

    # Band-pass filtering
    img = cv2.GaussianBlur(norm_image, (noise_length,noise_length), 0) - cv2.boxFilter(norm_image, -1, (cell_length,cell_length))
    img[img<0] = 0
    nimg = cv2.normalize(img, alpha = 255, beta = 0, norm_type = cv2.NORM_MINMAX)
    #nimg = img

    (cnts, _) = cv2.findContours(nimg.copy(), cv2.RETR_EXTERNAL,
                                 cv2.CHAIN_APPROX_SIMPLE)

    # loop over the contours
    n = 0
    for i, c in enumerate(cnts):
        # if the contour is too small, ignore it
        area = cv2.contourArea(c)
        (x, y, w, h) = cv2.boundingRect(c)
        if (area < 1000) or (area > 100000) or (w > 1000) or (h > 1000):
            continue

        n += 1
        cvalid = c

    print n

    if n == 1:
        c = cvalid

        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        print w, h, cv2.contourArea(c)
        # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.drawContours(frame, cnts, i, (0, 255, 0), 3)

        # Calculate moments / From this one could get the orientation
        M = cv2.moments(c)
        cx = M['m10'] / M['m00']
        cy = M['m01'] / M['m00']
        print cx, cy

        cv2.rectangle(frame, (int(cx) - 2, int(cy) - 2), (int(cx) + 2, int(cy) + 2), (0, 255, 0), 2)

    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    sleep(0.2)

cap.release()
cv2.destroyAllWindows()
