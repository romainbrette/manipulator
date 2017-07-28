'''
Tracking using Trackpy.

Not very fast but maybe ok if downscaled in size?
Apparently it's slow on the first call (compilation?)
Yes it's the numba engine! python better

The idea: in each frame, locate particles
Connect between two successive frames
Select the one that is moving
Or: select the one closest to the current position (=tracking)

Ideas:
use skimage
active contours?
elliptical Hough transform
'''
from __future__ import division, unicode_literals, print_function
import matplotlib as mpl
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
from pandas import DataFrame, Series  # for convenience
import cv2
from time import time

import pims
import trackpy as tp

from skimage.restoration import denoise_nl_means
from skimage.transform import hough_ellipse

#filename = '/Users/Romain/ownCloud/Paramecium/Comportement/pool_footage_2017_05_16/oldpool_raw.avi'
filename = '/Users/Romain/Desktop/paramecie 1.mov'

frames = pims.Video(filename)

print("starting")

previousx = None
previousy = None

for i in range(11,12):

    img = frames[i][:,:,0]

    #img = denoise_nl_means(img, 10)

    height, width = img.shape[:2]
    img = cv2.resize(img, (int(width/10),int(height/10))) # faster

    t1=time()
    f = tp.locate(img, 21, invert=True, minmass=3000, max_iterations = 1,
                  characterize=True, engine = 'python') # numba is too slow!
    #f = tp.locate(img, 201, invert=True, minmass=3000, max_iterations=1,
    #                            characterize=True, engine = 'python') # numba is too slow!
    t2=time()
    print(t2-t1)

    x = np.array(f['x'])
    y = np.array(f['y'])

    # Now we match to previous particles
    if previousx is not None:
        # Calculate distance matrix
        #print(np.dot(x.T,np.ones(len(previousx))))
        pass

    #fig, ax = plt.subplots()
    #ax.hist(f['mass'], bins=20)

    # Optionally, label the axes.
    #ax.set(xlabel='mass', ylabel='count')

    previousx = x
    previousy = y

plt.figure()
tp.annotate(f, img)

#plt.imshow(frames[0])

plt.show()
