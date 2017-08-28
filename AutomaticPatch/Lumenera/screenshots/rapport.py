import cv2

img = cv2.imread('screenshot2.jpg', 0)
img = cv2.bilateralFilter(img, 4, 10, 5)
img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
canny = cv2.Canny(img, 40, 50)


ret,thresh = cv2.threshold(canny,127,255,0)
im2,contours,hierarchy = cv2.findContours(thresh, 1, 2)
rows,cols = img.shape[:2]
for cnt in contours:
    M = cv2.moments(cnt)
    if (cv2.arcLength(cnt, True) > 90) & bool(M['m00']):
        [vx,vy,x,y] = cv2.fitLine(cnt, cv2.DIST_L2,0,0.01,0.01)
        lefty = int((-x*vy/vx) + y)
        righty = int(((cols-x)*vy/vx)+y)
        cv2.line(img,(cols-1,righty),(0,lefty),(0,255,0),2)

cv2.imwrite('contour.jpg', img)