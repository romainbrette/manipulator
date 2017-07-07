"""
Functions for camera
Use Micro Manager Py

Initialization of the cameras with micro manager
"""

import time
import sys
sys.path.append('C:\\Program Files\\Micro-Manager-1.4')
import MMCorePy

__all__ = ['camera_init', 'camera_unload']


def camera_init(camera_name):
    """
    Initializing the camera/microscope
    :return: mmc: microscope device, can be controlled using micro manager methods (see HAMAMATSU_CAMERA_METHODS.txt)
    """
    mmc = MMCorePy.CMMCore()

    if camera_name == 'Hamamatsu':
        mmc.loadDevice('Camera', 'HamamatsuHam', 'HamamatsuHam_DCAM')
        flip = [True, 2]
    elif camera_name == 'Lumenera':
        mmc.loadDevice('Camera', 'Lumenera', 'LuCam')
        flip = [True, 1]
    else:
        raise SystemError('Unknown camera.')

    mmc.initializeDevice('Camera')

    # To get the properties you can set on the camera:
    # print mmc.getDevicePropertyNames('Camera')

    mmc.setCameraDevice('Camera')
    mmc.setExposure(30)

    time.sleep(1)  # the microscope gives a wrong position in the very beginning, so wait a bit

    return mmc, flip


def camera_unload(mmc):
    """
    release the microscope
    """
    mmc.unloadDevice('Camera')
    pass
