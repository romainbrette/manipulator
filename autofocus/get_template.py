import cv2
import numpy as np


def get_template(img):
    """
    Get a template image of the tip around the center of an image for any angle of the tip.
    """

    width, height = img.shape[:2]
    ratio = 64

    template = img[width/2-width/ratio:width/2+width/ratio, height/2-height/ratio:height/2+height/ratio]

    width, height = template.shape[:2]
    weight = []
    for i in range(3):
        for j in range(3):
            temp = cv2.Canny(template[j*width/4:width/2+j*width/4, i*height/4:height/2+i*height/4], 100, 200)
            _, bin_edge = np.histogram(temp.flatten)
            #weight += [img.argmax()] ?
            weight += [bin_edge.max()]

    index = weight.index(max(weight))
    j = index%3
    i = index//3
    template = template[j*width/4:width/2+j*width/4, i*height/4:height/2+i*height/4]

    return template

def disp_template_zone(img):
    """
    Display the zone where the template image is taken
    :param img: image
    :return: img: image with a red rectangle and a red centered cross
    """
    width, height = img.shape[:2]
    ratio = 64
    pt1 = (width/2 - width/ratio, height/2 - height/ratio)
    pt2 = (width/2 + width/ratio, height/2 + height/ratio)
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

