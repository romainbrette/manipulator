import cv2

x_init = 50
y_init = 70


def mouse(event, x, y, flags, param):

    if event == cv2.EVENT_LBUTTONUP:
        print x_init-x, y_init-y

    pass

if __name__ == '__main__':
    img = cv2.imread('pipette.jpg', 0)
    cv2.namedWindow('Camera', flags=cv2.WINDOW_NORMAL)
    x_init = 50
    y_init = 70
    x = 0

    while 1:
        key = cv2.waitKey(1)
        x += 1
        y = 5

        if key & 0xFF == ord('q'):
            break

        cv2.imshow('Camera', img)
        cv2.setMouseCallback('Camera', mouse, {'test': x})

    cv2.destroyAllWindows()
