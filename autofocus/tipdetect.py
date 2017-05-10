'''
Pipette tip detection.

Adapted from Wu et al. (2011). Robust Automatic Focus Algorithm for Low Contrast Images
Using a New Contrast Measure
'''

import cv2
import numpy as np


__all__ = ['tip_detect']


def tip_detect(img):
    '''
    Detects the tip of a pipette in an image.
    This is just a corner detection algorithm.
    Probably works only with a clean (not noisy) image.

    Returns
    -------
    x,y : position of tip on image in pixels.
    criterion : maximum value of Corner-Harris algorithm.
    '''

    dst = cv2.cornerHarris(img, 2, 3, 0.04)

    n = dst.argmax()
    y, x = np.unravel_index(n, img.shape)
    criterion = dst.flatten()[n]

    return x,y,criterion


if __name__ == '__main__': # test
    img = cv2.imread('template.jpg', 0)
    x,y,_ = tip_detect(img)
    cv2.rectangle(img, (x-10, y-10), (x+10, y+10), (0, 0, 255))
    cv2.imshow('dst', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
