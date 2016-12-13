'''
Finding an image in another image.
Typically used to locate a pipette in an image, using a previous photo.
'''
import cv2
import time
import numpy as np

__all__ = ['find_template']

def find_template(img, template):
    '''
    Finds the template in the image.

    Returns
    -------
    x,y : position in pixels
    max_val : match performance
    '''
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    x, y = max_loc
    return x, y, max_val

if __name__ == '__main__': # test
    img = cv2.imread('pipette1.jpg', 0)
    height, width = img.shape
    cv2.imshow('Pipette',img)

    img2 = img[height*3/8:height*5/8,width*3/8:width*5/8]
    cv2.imshow('Template',img2)
    #img2 = np.zeros(img.shape)
    #img2[200:,300:] = img[:-200,:-300]

    print find_template(img, img2)

    key = cv2.waitKey(0)
    cv2.destroyAllWindows()
