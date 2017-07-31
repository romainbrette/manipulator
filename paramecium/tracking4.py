'''
Tracking using active contour.

There is a bounding box around the current position.
'''
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
from skimage import color, img_as_ubyte
from skimage.feature import canny
from skimage.transform import hough_ellipse
from skimage.draw import ellipse_perimeter
from skimage.filters import gaussian
from skimage.segmentation import active_contour

#filename = '/Users/Romain/ownCloud/Paramecium/Comportement/pool_footage_2017_05_16/oldpool_raw.avi'
#filename = '/Users/Romain/Desktop/paramecie 1.mov'
filename = '/Users/Romain/Desktop/zone_intrigante2.mp4'

length = 20 # approximate length of paramecium
width = 10
x,y = 330, 300 # initial guess
box = 50 # Bounding box

frames = pims.Video(filename)

img_rgb = frames[11][x-box/2:x+box/2,y-box/2:y+box/2,:]
img = img_rgb[:,:,0]

s = np.linspace(0, 2*np.pi, 100)
x = 20 + length*np.cos(s)
y = 20 + length*np.sin(s)
init = np.array([x, y]).T

snake = active_contour(img,init)#, alpha=0.015, beta=10, gamma=0.001)


fig = plt.figure()
ax = fig.add_subplot(111)
plt.imshow(img_rgb)#, cmap=plt.cm.gray)
ax.plot(init[:, 0], init[:, 1], '--r', lw=3)
ax.plot(snake[:, 0], snake[:, 1], '-b', lw=3)
plt.show()
