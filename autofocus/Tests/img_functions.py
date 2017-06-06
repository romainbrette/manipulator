import cv2

def disp_template_zone(img):
    """
    Display the zone where the template image is taken
    :param img: image
    :return: img: image with a red rectangle
    """
    img = img.copy()
    height, width = img.shape[:2]
    ratio = 32
    pt1 = (width/2 - 3*width/ratio, height/2 - 3*height/ratio)
    pt2 = (width/2 + 3*width/ratio, height/2 + 3*height/ratio)
    cv2.rectangle(img, pt1, pt2, (0, 0, 255))

    return img


def disp_centered_cross(img):

    img = img.copy()
    height, width = img.shape[:2]
    cv2.line(img, (width / 2 + 10, height / 2), (width / 2 - 10, height / 2), (0, 0, 255))
    cv2.line(img, (width / 2, height / 2 + 10), (width / 2, height / 2 - 10), (0, 0, 255))

    return img
