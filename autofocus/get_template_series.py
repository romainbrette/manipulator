import cv2
import numpy as np
from get_img import *

__all__ = ['get_template_series', 'disp_template_zone', 'disp_centered_cross']


def get_template_series(microscope, nb_images, cam):
    """
    Get a series of template images of the tip around the center of an image for any angle of the tip.
    :param microscope: XYZUnit device controlling the microscope
    :param nb_images: number of template images to take, must be odd so an even number of images at each side is taken
    :param cam: micro manager camera
    """

    template_series = []
    temp = []

    frame = get_img(microscope, cam)
    height, width = frame.shape[:2]
    ratio = 32

    template = frame[height/2-3*height/ratio:height/2+3*height/ratio, width/2-3*width/ratio:width/2+3*width/ratio]
    height, width = template.shape[:2]
    weight = []
    template = cv2.bilateralFilter(template, 9, 75, 75)
    for i in range(3):
        for j in range(3):
            temp = template[i*height/4:height/2+i*height/4, j*width/4:width/2+j*width/4]
            bin_edge, _ = np.histogram(temp.flatten())
            weight += [bin_edge.min()]

    index = weight.index(max(weight))
    j = index % 3
    i = index // 3
    template_loc = [temp.shape[1] * (1 - j/2.), temp.shape[0] * (1 - i/2.)]

    pos = microscope.position(2)

    for k in range(nb_images):
        frame = get_img(microscope, cam, pos-(nb_images-1)/2+k)
        height, width = frame.shape[:2]
        cv2.imshow('Camera', frame)
        cv2.waitKey(1)
        img = frame[height / 2 - 3 * height / ratio:height / 2 + 3 * height / ratio,
                    width / 2 - 3 * width / ratio:width / 2 + 3 * width / ratio]
        height, width = img.shape[:2]
        img = img[i * height / 4:height / 2 + i * height / 4, j * width / 4:width / 2 + j * width / 4]
        template_series += [img]

    _ = get_img(microscope, cam, pos)

    cv2.imshow('template', template_series[2])

    return template_series, template_loc


def disp_template_zone(img):
    """
    Display the zone where the template image is taken
    :param img: image
    :return: img: image with a red rectangle
    """
    height, width = img.shape[:2]
    ratio = 32
    pt1 = (width/2 - 3*width/ratio, height/2 - 3*height/ratio)
    pt2 = (width/2 + 3*width/ratio, height/2 + 3*height/ratio)
    cv2.rectangle(img, pt1, pt2, (0, 0, 255))

    return img


def disp_centered_cross(img):

    height, width = img.shape[:2]
    cv2.line(img, (width / 2 + 10, height / 2), (width / 2 - 10, height / 2), (0, 0, 255))
    cv2.line(img, (width / 2, height / 2 + 10), (width / 2, height / 2 - 10), (0, 0, 255))

    return img

if __name__ == '__main__':
    from matplotlib import pyplot as plt

    img = cv2.imread('template.jpg', 0)
    img = cv2.Canny(img[0:43, 0:43], 100, 200)
    histo, _ = np.histogram(img.flatten())
    print img.argmax()
    cv2.imshow('test', img)
    plt.plot(histo)
    plt.show()
    cv2.destroyAllWindows()
