import cv2
from Hamamatsu_camera import *

def stop_device(devtype, dev, microscope, cap):
    if devtype == 'SM5':
        microscope.stopSequenceAcquisition()
        camera_unload(microscope)
        microscope.reset()
    elif devtype == 'SM10':
        cap.release()

    cv2.destroyAllWindows()
    del dev