"""
Search a template image in an other image
Not scale nor rotation invariant
"""

import cv2

__all__ = ['templatematching']

def templatematching(img, template):

    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    _, maxval, _, maxloc = cv2.minMaxLoc(res)

    threshold = 0.8

    if maxval >= threshold:
        is_in = 1
    else:
        is_in = 0

    x, y = maxloc[:2]

    return is_in, x, y


if __name__ == '__main__':
    img = cv2.imread('pipette.jpg')
    template = cv2.imread('template.jpg')
    res, x, y = templatematching(img, template)
    print res
    if res:
        h = template.shape[1]
        w = template.shape[0]
        cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255))
    cv2.imshow("camera", img)

    cv2.destroyAllWindows()