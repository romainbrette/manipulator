import cv2
from numpy import matrix

__all__ = ['clic_position']


def clic_position(event, x, y, calibrated, mat, x_init, y_init, um_px, microscope, arm, init_pos_m, init_pos_a):

    if calibrated:
        if event == cv2.EVENT_LBUTTONUP:
            pos = matrix('0.; 0.; 0.')
            for i in range(3):
                pos[i, 0] = microscope.position(i) - init_pos_m[i]

            pos[0, 0] += (x_init - x) * um_px
            pos[1, 0] += (y_init - y) * um_px

            move = mat*pos
            for i in range(3):
                arm.absolute_move(init_pos_a[i]+move[i], i)

    pass
