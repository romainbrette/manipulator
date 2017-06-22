'''
Creates a photo mosaic using the stage
'''
from devices import *
from serial import SerialException
from AutomaticPatch.Camera.camera_init import *
from pylab import *
import cv2

from os.path import expanduser
home = expanduser("~")

SM5 = True

try:
    if SM5:
        dev = LuigsNeumann_SM5('COM3')
    else:
        dev = LuigsNeumann_SM10()
except SerialException:
    print "L&N not found. Falling back on fake device."
    dev = FakeDevice()

"""
if SM5:
    microscope_Z = Leica('COM1')
    microscope = XYMicUnit(dev, microscope_Z, [7, 8])
else:
    microscope = XYZUnit(dev, [7, 8, 9])
"""
microscope = XYZUnit(dev, [7,8])

print "Device initialized"

mmc = camera_init('SM5')

# We first need to calibrate the stage
# Then we take a series of photos

frames = []

for j in range(5):
    for i in range(10):
        microscope.relative_move(200., axis = 0)
        microscope.wait_motor_stop(axis = 0)
        mmc.snapImage()
        frames.append(mmc.getImage())
    microscope.relative_move(200., axis = 1)
    microscope.wait_motor_stop(axis=1)
    mmc.snapImage()
    frames.append(mmc.getImage())
    for i in range(10):
        microscope.relative_move(-200., axis = 0)
        microscope.wait_motor_stop(axis = 0)
        mmc.snapImage()
        frames.append(mmc.getImage())

camera_unload(mmc)

for i in enumerate(frames):
    cv2.imwrite(home+'/mosaic'+str(i)+'.jpg')

"""
for frame in frames[:10]:
    imshow(frame, cmap='gray')
    show()
"""
