"""
Search a template image in an other image
Not scale nor rotation invariant
"""

import cv2
import numpy as np

__all__ = ['templatematching']

def templatematching(img, template):
    """
    Search a template image in an other image
    Not scale nor rotation invariant
    :param img: image to look in
    :param template: image to look for
    :return: is_in: 1 if the template has been detected, 0 otherwise
             maxval: maximum value corresponding to the best matching ratio
             maxloc: location (x,y) in the image of maxval
    """

    # Searching for a template match using cv2.TM_COEFF_NORMED detection
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)

    # Getting maxval and maxloc
    _, maxval, _, maxloc = cv2.minMaxLoc(res)

    # Threshold for maxval to assure a good template matching
    threshold = 0.75

    if maxval >= threshold:
        is_in = 1
    else:
        is_in = 0

    return is_in, maxval, maxloc


if __name__ == '__main__':
    img = cv2.imread('pipette.jpg', 0)
    template = cv2.imread('template.jpg', 0)
    res, val, loc = templatematching(img, template)
    x, y = loc[:2]
    if res:
        h = template.shape[1]
        w = template.shape[0]
        cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255))
    cv2.imshow("camera", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()