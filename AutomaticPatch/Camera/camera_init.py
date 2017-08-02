"""
Functions for camera
Use Micro Manager Py

Initialization of the cameras with micro manager
"""

import sys
import warnings
sys.path.append('C:\\Program Files\\Micro-Manager-1.4')
try:
    import MMCorePy
except ImportError:
    # Micromanager not installed
    warnings.warn('Micromanager is not installed.')

__all__ = ['camera_init', 'camera_unload']


def camera_init(camera_name):
    """
    Initializing the camera
    :return: mmc: microscope device, can be controlled using micro manager methods (see HAMAMATSU_CAMERA_METHODS.txt)
    """
    mmc = MMCorePy.CMMCore()

    if camera_name == 'Hamamatsu':
        mmc.loadDevice('Camera', 'HamamatsuHam', 'HamamatsuHam_DCAM')
        flip = [True, 2]
        exposure = 60
    elif camera_name == 'Lumenera':
        mmc.loadDevice('Camera', 'Lumenera', 'LuCam')
        flip = [True, 1]
        exposure = 30
    else:
        raise SystemError('Unknown camera.')

    mmc.initializeDevice('Camera')
    mmc.setCameraDevice('Camera')
    mmc.setExposure(exposure)

    # To get the properties you can set on the camera:
    # print mmc.getDevicePropertyNames('Camera')

    return mmc, flip


def camera_unload(mmc):
    """
    release the microscope
    """
    mmc.unloadDevice('Camera')
    pass
