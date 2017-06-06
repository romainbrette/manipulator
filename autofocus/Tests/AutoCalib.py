from patch_clamp_robot import *

robot = PatchClampRobot('SM5', 'dev1')

while 1:

    robot.show()
    robot.enable_clic_position()
    key = cv2.waitKey(1)

    if key & 0xFF == ord('q'):
        break

    if key & 0xFF == ord('b'):
        calibrated = robot.calibrate()
        if not calibrated:
            print 'Calibration canceled.'

del robot
