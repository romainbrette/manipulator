import cv2
from Hamamatsu_camera import *


def stop_device(devtype, dev, microscope, cap):
    if devtype == 'SM5':
        cap.stopSequenceAcquisition()
        camera_unload(cap)
        cap.reset()
        del microscope
    elif devtype == 'SM10':
        cap.stopSequenceAcquisition()
        camera_unload(cap)
        cap.reset()
        del microscope
        #cap.release()

    cv2.destroyAllWindows()
    del dev
    pass
