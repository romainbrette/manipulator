import cv2
from Hamamatsu_camera import *

def stop_device(dev, microscope, cam):

    cam.stopSequenceAcquisition()
    camera_unload(cam)
    cam.reset()
    del microscope
    cv2.destroyAllWindows()
    del dev
    pass
