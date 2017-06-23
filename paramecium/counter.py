'''
Paramecium counter

check this
https://github.com/opencv/opencv_attic/blob/master/opencv/samples/cpp/fitellipse.cpp
https://stackoverflow.com/questions/42206042/ellipse-detection-in-opencv-python
http://docs.opencv.org/3.1.0/dd/d49/tutorial_py_contour_features.html
'''
import matplotlib.pyplot as plt
from skimage import data, color, img_as_ubyte
from skimage.io import imread
from skimage.feature import canny
from skimage.transform import hough_ellipse
from skimage.draw import ellipse_perimeter

filename = "/Users/Romain/Dropbox/Projects/New computational neuroscience/Biological models/Paramecium/Experiments/paramecie in drop on agar.jpg"

img = imread(filename)
image_gray = imread(filename, as_grey = True)
edges = canny(image_gray, sigma=2.0,low_threshold=0.55, high_threshold=0.8)

result = hough_ellipse(edges, accuracy=20, threshold=250,min_size=100, max_size=120)
result.sort(order='accumulator')

# Estimated parameters for the ellipse
best = list(result[-1])
yc, xc, a, b = [int(round(x)) for x in best[1:5]]
orientation = best[5]

# Draw the ellipse on the original image
cy, cx = ellipse_perimeter(yc, xc, a, b, orientation)
img[cy, cx] = (0, 0, 255)
# Draw the edge (white) and the resulting ellipse (red)
edges = color.gray2rgb(img_as_ubyte(edges))
edges[cy, cx] = (250, 0, 0)

fig2, (ax1, ax2) = plt.subplots(ncols=2, nrows=1, figsize=(8, 4), sharex=True,
                                sharey=True,
                                subplot_kw={'adjustable':'box-forced'})

ax1.set_title('Original picture')
ax1.imshow(img)

ax2.set_title('Edge (white) and result (red)')
ax2.imshow(edges)


#img = cv2.medianBlur(img,11)
#edges = cv2.Canny(img,10,80)
#th = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,15,2)
#contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
#cv2.drawContours(edges,contours,0,(0,0,255))

#plt.imshow(img, cmap='gray')
#plt.axis('off')
ax2.show()

#cv2.imshow('Image', img)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
