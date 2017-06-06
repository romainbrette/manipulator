from patch_clamp_robot import *

robot = PatchClampRobot('SM5', 'dev1')
calibrated = 0
while 1:

    robot.show()
    key = cv2.waitKey(1)

    if key & 0xFF == ord('q'):
        break

    if key & 0xFF == ord('b'):
        calibrated = robot.calibrate()
        if not calibrated:
            print 'Calibration canceled.'
    if calibrated:
        robot.enable_clic_position()

del robot
