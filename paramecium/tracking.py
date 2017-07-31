'''
Tracking using Trackpy.

The idea: in each frame, locate particles
Connect between two successive frames
Select the one that is moving
Or: select the one closest to the current position (=tracking)

'''
import matplotlib as mpl
import matplotlib.pyplot as plt

import numpy as np
from time import sleep
import pandas as pd
from pandas import DataFrame, Series  # for convenience
import cv2
from time import time
import imageio

import pims
import trackpy as tp

from skimage.restoration import denoise_nl_means
from skimage.transform import hough_ellipse

#filename = '/Users/Romain/ownCloud/Paramecium/Comportement/pool_footage_2017_05_16/oldpool_raw.avi'
#filename = '/Users/Romain/Desktop/paramecie 1.mov'
#filename = '/Users/Romain/Desktop/zone_intrigante2.mp4'
filename = '/Users/Romain/Desktop/gouttelette2.mp4'

#frames = pims.Video(filename)
#cap = cv2.VideoCapture(filename)
reader = imageio.get_reader(filename)

print("starting")

#x,y = 330, 300 # initial guess
x,y = 500, 390
#box = 100 # Bounding box
box = 400

diameter = 51 #21

for frame in reader:
#while(True):
    #_, frame = cap.read()
    #height, width = frame.shape[:2]
    #frame = cv2.resize(frame, (int(width/10),int(height/10))) # faster

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


    #print x,y
#for i in range(11,12):

#    img = frames[i][:,:,0]
#    print(img.shape)

    #img = denoise_nl_means(img, 10)

    img = img[(y - box / 2):(y + box / 2), (x - box / 2):(x + box / 2)]

    t1=time()
    f = tp.locate(img, diameter, noise_size=2, invert=True, minmass=1000, max_iterations = 1,
                  characterize=True, engine = 'python') # numba is too slow!
    #f = tp.locate(img, 201, invert=True, minmass=3000, max_iterations=1,
    #                            characterize=True, engine = 'python') # numba is too slow!
    t2=time()
    #print(t2-t1)

    xp = np.array(f['x'])
    yp = np.array(f['y'])

    # Closest one
    if len(xp)>0:
        j=np.argmin((xp-box/2)**2+(yp-box/2)**2)
        xt,yt= xp[j],yp[j]

    #fig, ax = plt.subplots()
    #ax.hist(f['mass'], bins=20)

        #cv2.rectangle(frame, (int(x+xt) - 2, int(y+yt) - 2), (int(x+xt) + 2, int(y+yt) + 2), (0, 255, 0), 2)
        cv2.rectangle(frame, (x-box/2,y-box/2), (x+box/2, y+box/2), (0, 255, 0), 2)
        cv2.rectangle(img, (int(xt) - 2, int(yt) - 2), (int(xt) + 2, int(yt) + 2), 255, 2)
        print xt,yt

        x = int(x-box/2+xt)
        y = int(y-box/2+yt)

    # Optionally, label the axes.
    #ax.set(xlabel='mass', ylabel='count')
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    #sleep(0.1)

#cap.release()
cv2.destroyAllWindows()

plt.figure()
#tp.annotate(f, img)

plt.imshow(frame)

plt.show()
