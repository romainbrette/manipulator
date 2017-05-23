'''
Tracking algorithm to keep the tip in focus during a move
Use the template matching method to focus
'''

#from template_focus import *
from focus_template_series import *
from template_matching import *
from get_img import *
import cv2


__all__ = ['focus_track']


def focus_track(devtype, microscope, arm, template, step, axis, alpha, um_px, estim=0, estim_loc=(0.,0.), cap=None):
    """
    Focus after a move of the arm
    """

    if devtype == 'SM5':
        pos = microscope.getPosition()
    else:
        pos = microscope.position(2)
    frame, img = getImg(devtype, microscope, cv2cap=cap, update=1)

    # Get initial location of the tip
    _, _, initloc = templatematching(img, template[len(template)/2])

    # Move the arm
    arm.relative_move(step, axis)
    frame, img = getImg(devtype, microscope, cv2cap=cap, update=1)
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

    # Move the platform to center the tip
    for i in range(2):
        microscope.relative_move(alpha[i]*estim_loc[i]*step, i)

    # Update the frame. Must be the next image
    frame, img = getImg(devtype, microscope, cv2cap=cap, update=1)
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

    frame, img = getImg(devtype, microscope, pos + estim * step, cv2cap=cap)
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)
    # Focus around the estimated focus height
    _, estim_temp, loc, frame = focus(devtype, microscope, template, cap)
    # MOVE THE PLATFORM TO COMPENSATE ERROR AND UPDATE FRAME
    for i in range(2):
        microscope.relative_move(alpha[i]*(loc[i] - initloc[i])*um_px, i)

    frame, img = getImg(devtype, microscope, cv2cap=cap, update=1)
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

    _, _, errloc = templatematching(img, template[len(template) / 2])
    errloc = [errloc[i] - initloc[i] for i in range(2)]
    err = (errloc[0]**2+errloc[1]**2)**0.5

    '''
    if err > 10:
        um_px += err / ((loc[0] - initloc[0])**2+(loc[1] - initloc[1])**2)**0.5
        print 'um_px corr'
        for i in range(2):
            microscope.relative_move(alpha[i]*errloc[i]*um_px, i)
    '''
    '''
        if devtype == 'SM5':
            microscope.setRelativePosition(estim*step)
        else:
            # PROBLEM WITH MICROSCOPE IF RELATIVE MOVE IS -8
            if estim*step != -8:
                microscope.relative_move(estim*step, 2)
            else:
                for i in range(2):
                    microscope.relative_move(-4, 2)
    '''

    # Update the estimated move to do for a move of 1 um of the arm
    estim += float(estim_temp)/float(step)
    print estim
    loc = [estim_loc[i] + (loc[i]-initloc[i])*um_px/float(step) for i in range(2)]

    return estim, loc, frame