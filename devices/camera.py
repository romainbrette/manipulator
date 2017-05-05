import time
import sys
import numpy as np
import matplotlib.pyplot as plt

# Demonstration how to use the Hamamatsu camera and the Leica Z-drive via Micro-Manager

sys.path.append('C:\\Program Files\\Micro-Manager-1.4')
import MMCorePy

print "Setting up camera and microscope...",
mmc = MMCorePy.CMMCore()
mmc.loadDevice('Camera', 'HamamatsuHam', 'HamamatsuHam_DCAM')
mmc.loadDevice('COM1', 'SerialManager', 'COM1')
mmc.setProperty('COM1', 'AnswerTimeout', 500.0)
mmc.setProperty('COM1', 'BaudRate', 19200)
mmc.setProperty('COM1','DelayBetweenCharsMs',0.0)
mmc.setProperty('COM1','Handshaking','Off')
mmc.setProperty('COM1','Parity','None')
mmc.setProperty('COM1','StopBits',1)
mmc.setProperty('COM1','Verbose',1)
mmc.loadDevice('Scope', 'LeicaDMI', 'Scope')
mmc.loadDevice('FocusDrive', 'LeicaDMI', 'FocusDrive')
mmc.setProperty('Scope', 'Port', 'COM1')
mmc.initializeDevice('Camera')
mmc.initializeDevice('COM1')
mmc.initializeDevice('Scope')
mmc.initializeDevice('FocusDrive')
print "done"

# To get the properties you can set on the camera:
print mmc.getDevicePropertyNames('Camera')


mmc.setCameraDevice('Camera')
mmc.setFocusDevice('FocusDrive')
mmc.setExposure(50)

# To continuously take pictures, use the following
# (pictures will be stored in a ring buffer, use mmc.getLastImage()
# to get the most recent image, or mmc.popNextImage() to get the
# next image in order and remove it from the buffer)
#mmc.startContinuousSequenceAcquisition(0)


time.sleep(1)  # the microscope gives a wrong position in the very beginning, so wait a bit

frames = []

print mmc.getPosition()
mmc.setRelativePosition(-50)
time.sleep(1)
print mmc.getPosition()

for _ in range(10):
    mmc.snapImage()
    frames.append(mmc.getImage())
    mmc.setRelativePosition(10)
    time.sleep(1)
    print mmc.getPosition()

mmc.unloadDevice('FocusDrive')
mmc.unloadDevice('Scope')
mmc.unloadDevice('Camera')

for i, frame in enumerate(frames):
    plt.subplot(3, 4, i+1)
    plt.imshow(frame, cmap='gray')
    plt.axis('off')
plt.tight_layout()
plt.show()

