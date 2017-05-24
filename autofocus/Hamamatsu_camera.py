"""
Functions for HAMAMATSU camera
Use Micro Manager Py
"""

import time
import sys
import MMCorePy
sys.path.append('C:\\Program Files\\Micro-Manager-1.4')


__all__ = ['camera_init', 'camera_unload']


def camera_init():
    """
    Initializing the camera/microscope
    :return: mmc: microscope device, can be controlled using micro manager methods (see HAMAMATSU_CAMERA_METHODS.txt)
    """

    print "Setting up camera and microscope...",
    mmc = MMCorePy.CMMCore()
    mmc.loadDevice('Camera', 'HamamatsuHam', 'HamamatsuHam_DCAM')
    mmc.initializeDevice('Camera')
    print "done"

    # To get the properties you can set on the camera:
    # print mmc.getDevicePropertyNames('Camera')

    mmc.setCameraDevice('Camera')
    mmc.setExposure(15)

    time.sleep(1)  # the microscope gives a wrong position in the very beginning, so wait a bit

    return mmc


def camera_unload(mmc):
    """
    release the microscope
    """
    mmc.unloadDevice('Camera')
    pass
