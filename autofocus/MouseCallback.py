import cv2
from numpy import matrix

__all__ = ['clic_position']


def clic_position(event, x, y, flags, param):
    """
    :param event: 
    :param x: 
    :param y: 
    :param flags: 
    :param param: {calibrated, mat, x_init, y_init, um_px, microscope, arm, init_pos_m, init_pos_a})
    :return: 
    """

    if param['calibrated']:
        if event == cv2.EVENT_LBUTTONUP:
            pos = matrix('0.; 0.; 0.')
            for i in range(3):
                pos[i, 0] = param['mic'].position(i) - param['init_mic'][i]

            temp = matrix([[(param['x_init'] - x + param['loc'][0]) * param['um_px']],
                           [(param['y_init'] - y + param['loc'][1]) * param['um_px']]])
            temp = param['alpha']*temp
            pos[0, 0] += temp[0, 0]
            pos[1, 0] += temp[1, 0]

            move = param['mat']*pos
            for i in range(3):
                param['arm'].absolute_move(param['init_arm'][i]+move[i], i)

    pass