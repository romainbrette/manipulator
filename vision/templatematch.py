'''
Finding an image in another image.
Typically used to locate a pipette in an image, using a previous photo.
'''
import cv2
import time

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
    img = cv2.imread('pipette.jpg', 0)
    img2 = img[20:100,10:100]
    t1 = time.time()
    print find_template(img, img2)
    t2 = time.time()
    print t2-t1
