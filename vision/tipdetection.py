'''
Pipette tip detection.

Adapted from Wu et al. (2011). Robust Automatic Focus Algorithm for Low Contrast Images
Using a New Contrast Measure

Maybe equalize with cv2.createCLAHE
and denoise
'''
import cv2
import numpy as np
import copy
import math

__all__ = ['tip_detection','genericFourtyXPipetteDetection']

def tip_detection(img):
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

### From Autopatcher_IG
## Really slow!
def genericFourtyXPipetteDetection(img):
    '''
    Returns
    -------
    y, x : tip position in pixels
    distance : minimum distance of tip to detected lines
    '''
    #height, width = img.shape
    edges = cv2.Canny(img, 30, 100)
    minimum_length = 15;

    while 1:
        linecount = 0;
        lines_unsorted = cv2.HoughLines(edges, 1, np.pi / 180, minimum_length)[0]

        # count lines
        for rho, theta in lines_unsorted:
            linecount = linecount + 1;
        # print rho, theta

        if linecount > 10:
            minimum_length = minimum_length + 1;
            continue

        # create cartesian matrix for each line
        # ax + by + c = 0    b is set to 1 and not being recorded
        cartesian_line = copy.deepcopy(lines_unsorted)
        for index, [rho, theta] in enumerate(lines_unsorted):
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))
            a = y1 - y2;
            b = x2 - x1;
            c = x1 * y2 - x2 * y1;
            a = a / b;
            c = c / b;
            cartesian_line[index] = [a, c]

        # cv2.imshow('edges', edges)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        lines = lines_unsorted

        black_board = np.zeros((img.shape[0], img.shape[1]), np.uint8)
        for index, [rho, theta] in enumerate(lines):
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))
            temp = np.zeros((img.shape[0], img.shape[1]), np.uint8)
            black_board = black_board + temp;
        # aftermath = aftermath + 1

        # cv2.imshow('black_board with lines', black_board)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        tip_x = 0;
        tip_y = 0;
        minimum_distance = 99999999999;  # has to be big
        current_distance = 0;
        cumulative_distance = 0;

        # calculate the distance to each line
        for x, col in enumerate(edges):
            for y, val in enumerate(col):
                cumulative_distance = 0
                if val != 0:
                    for index, [a, c] in enumerate(cartesian_line):
                        distance = abs(a * y + x + c) / (math.sqrt(a * a + 1))
                        cumulative_distance = cumulative_distance + distance
                    if cumulative_distance < minimum_distance:
                        tip_x = x;
                        tip_y = y;
                        minimum_distance = cumulative_distance;
            # print "the minimum distance is ", minimum_distance
            coordinate = (tip_y, tip_x);
        #cv2.circle(edges, coordinate, 2, (255, 255, 255), 2)

        #cv2.imshow('edges', edges)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

        return [tip_y, tip_x, minimum_distance]
        break

    pass


if __name__ == '__main__': # test
    img = cv2.imread('pipette.jpg', 0)
    x,y,_ = tip_detection(img)
    #genericFourtyXPipetteDetection(img)
    cv2.circle(img, (x, y), 2, (155, 0, 25))
    cv2.imshow('dst', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
