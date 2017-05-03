'''
Focusing the tip using tipdetect
Work only if the tip is well detected at first
'''

from devices import *
from tipdetect import *
import cv2
from scipy.optimize import minimize_scalar


def getImg(z, microscope):
    '''
    get an image from the microscope at given height z
    '''

    cap = cv2.VideoCapture(0)

    microscope.absolute_move(z, 2)

    # Capture frame
    ret, frame = cap.read()

    # frame has to be encoded to an usable image to use tipdetect
    _, img = cv2.imencode('.jpg', frame)
    return cv2.imdecode(img, 0)

def tipfocus(microscope):
    '''
    Focus on the tip around the current height.
    The tip should be nearly in focus.
    '''

    current_z = microscope.position(2)
    mini = current_z - 20
    maxi = current_z + 20

    #  Using the maximum value of Corner-Harris algorithm
    minimize_scalar(lambda x : -tip_detect(getImg(x, microscope))[2], bounds=(mini, maxi),
                    method='Bounded')
    pass

if __name__ == '__main__':
    from serial import SerialException
    try:
        dev = LuigsNeumann_SM10()
    except SerialException:
        print "L&N SM-10 not found. Falling back on fake device."
        dev = FakeDevice()

    microscope = XYZUnit(dev, [7, 8, 9])
    tipfocus(microscope)
    del dev