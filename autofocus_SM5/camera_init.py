import time
import sys

sys.path.append('C:\\Program Files\\Micro-Manager-1.4')
import MMCorePy

__all__ = ['camera_init', 'camera_unload']


def camera_init():

    print "Setting up camera and microscope...",
    mmc = MMCorePy.CMMCore()
    mmc.loadDevice('Camera', 'HamamatsuHam', 'HamamatsuHam_DCAM')
    #mmc.loadDevice('Camera', 'OpenCVgrabber', 'OpenCVgrabber')
    mmc.loadDevice('COM1', 'SerialManager', 'COM1')
    mmc.setProperty('COM1', 'AnswerTimeout', 500.0)
    mmc.setProperty('COM1', 'BaudRate', 19200)
    mmc.setProperty('COM1', 'DelayBetweenCharsMs', 0.0)
    mmc.setProperty('COM1', 'Handshaking', 'Off')
    mmc.setProperty('COM1', 'Parity', 'None')
    mmc.setProperty('COM1', 'StopBits', 1)
    mmc.setProperty('COM1', 'Verbose', 1)
    mmc.loadDevice('Scope', 'LeicaDMI', 'Scope')
    mmc.loadDevice('FocusDrive', 'LeicaDMI', 'FocusDrive')
    mmc.setProperty('Scope', 'Port', 'COM1')
    mmc.initializeDevice('Camera')
    mmc.initializeDevice('COM1')
    mmc.initializeDevice('Scope')
    mmc.initializeDevice('FocusDrive')
    print "done"

    # To get the properties you can set on the camera:
    # print mmc.getDevicePropertyNames('Camera')


    mmc.setCameraDevice('Camera')
    mmc.setFocusDevice('FocusDrive')
    mmc.setExposure(50)

    time.sleep(1)  # the microscope gives a wrong position in the very beginning, so wait a bit

    return mmc


def camera_unload(mmc):
    mmc.unloadDevice('FocusDrive')
    mmc.unloadDevice('Scope')
    mmc.unloadDevice('Camera')
    pass