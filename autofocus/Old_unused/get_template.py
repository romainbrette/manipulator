"""
NOT USED ANYMORE TAKE ONE IMAGE WITHOUT RETURNING TIP POSITION 
"""

import cv2
import numpy as np


def get_template(img):
    """
    Get a template image of the tip around the center of an image for any angle of the tip.
    """

    height, width = img.shape[:2]
    ratio = 32

    template = img[height/2-3*height/ratio:height/2+3*height/ratio, width/2-3*width/ratio:width/2+3*width/ratio]
    height, width = template.shape[:2]
    weight = []
    for i in range(3):
        for j in range(3):
            temp = template[i*height/4:height/2+i*height/4, j*width/4:width/2+j*width/4]
            bin_edge, _ = np.histogram(temp.flatten())
            #weight += [temp.argmax()]
            weight += [bin_edge.max()]

    index = weight.index(max(weight))
    index = 5
    j = index%3
    i = index//3
    template = template[i*height/4:height/2+i*height/4, j*width/4:width/2+j*width/4]

    return template

def disp_template_zone(img):
    """
    Display the zone where the template image is taken
    :param img: image
    :return: img: image with a red rectangle and a red centered cross
    """
    height, width = img.shape[:2]
    ratio = 32
    pt1 = (width/2 - 3*width/ratio, height/2 - 3*height/ratio)
    pt2 = (width/2 + 3*width/ratio, height/2 + 3*height/ratio)
    cv2.rectangle(img, pt1, pt2, (0, 0, 255))
    cv2.line(img, (width / 2 + 10, height / 2), (width / 2 - 10, height / 2), (0, 0, 255))
    cv2.line(img, (width / 2, height / 2 + 10), (width / 2, height / 2 - 10), (0, 0, 255))

    return img

if __name__ == '__main__':
    from matplotlib import pyplot as plt

    img = cv2.imread('template.jpg', 0)
    img = cv2.Canny(img[0:43,0:43], 100, 200)
    histo, _ = np.histogram(img.flatten())
    print img.argmax()
    cv2.imshow('test', img)
    plt.plot(histo)
    plt.show()
    cv2.destroyAllWindows()
