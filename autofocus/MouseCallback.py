import cv2
from numpy import matrix
from numpy.linalg import inv

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

            temp = inv(param['alpha']) * matrix([[(param['x_init'] - x + param['loc'][0]) * param['um_px']],
                                                [(param['y_init'] - y + param['loc'][1]) * param['um_px']]])
            pos[0, 0] += temp[0, 0]
            pos[1, 0] += temp[1, 0]

            move = param['mat']*pos
            reversedrange = range(3)
            reversedrange.reverse()
            for i in reversedrange:
                param['arm'].absolute_move(param['init_arm'][i]+move[i], i)

    pass
