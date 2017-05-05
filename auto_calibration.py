"""
Automated calibration of the manipulator
"""

from autofocus import *
from devices import *
import cv2
from math import atan2
from serial import SerialException

# Capture Video input
cap = cv2.VideoCapture(0)
cv2.namedWindow('Camera')

# Devices to control
try:
    dev = LuigsNeumann_SM10()
except SerialException:
    print "L&N SM-10 not found. Falling back on fake device."
    dev = FakeDevice()

microscope = XYZUnit(dev, [7, 8, 9])
arm = XYZUnit(dev, [1, 2, 3])

init_pos_m = (microscope.position(0), microscope.position(1), microscope.position(2))
init_pos_a = (arm.position(0), arm.position(1), arm.position(2))

# step case
step = -1

frame, img = getImg(cap)
while 1:

    key = cv2.waitKey(1)

    if step == -1:
        if key & 0xFF == ord('b'):
            step += 1
    elif step == 0:
        tipfocus(microscope, cap)
        x0, y0, c = tip_detect(img)
        focus_track(arm, 50, 0, microscope, cap) # refaire ici pour rafraichir l'affichage durant le mouvement
        step += 1
    elif step == 1:
        x1, y1, c = tip_detect(img)
        z_diff = microscope.position(2) - init_pos_m[2]
        theta1 = atan2((50**2-z_diff**2)**0.5, z_diff)
        theta2 = atan2(y1-y0, x1-x0)
        arm.relative_move(50, 1)
        step += 1
        print theta1
    elif step == 2:
        x2, y2, c = tip_detect(img)
        microscope.relative_move(50, 0)
        step += 1
    elif step == 3:
        x3, y3, c = tip_detect(img)
        microscope.relative_move(50, 1)
        step += 1
    else:
        pass


    frame, img = cap.read()

    cv2.imshow('Camera', frame)