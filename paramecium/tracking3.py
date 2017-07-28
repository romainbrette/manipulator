'''
Tracking using features
- apparently not appropriate
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

    # Band-pass filtering
    #gray = cv2.GaussianBlur(gray, (noise_length,noise_length), 0)# - cv2.boxFilter(gray, -1, (cell_length,cell_length))
    #gray = -gray
    #img[img<0] = 0

    if (previous is None):
        previous = gray
        continue

    orb = cv2.ORB()
    kp1, des1 = orb.detectAndCompute(previous, None)
    kp2, des2 = orb.detectAndCompute(gray, None)

    img2 = cv2.drawKeypoints(frame, kp2, color=(0, 255, 0), flags=0)

    '''
    # create BFMatcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # Match descriptors.
    matches = bf.match(des1, des2)

    # Sort them in the order of their distance.
    matches = sorted(matches, key=lambda x: x.distance)
    '''

    cv2.imshow('frame',img2)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    sleep(0.2)

cap.release()
cv2.destroyAllWindows()
