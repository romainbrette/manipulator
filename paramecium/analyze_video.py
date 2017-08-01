'''
Analyze a Paramecium video for tracking
'''
import matplotlib.pyplot as plt
import numpy as np
import cv2
from time import time, sleep
import imageio
import trackpy as tp

#filename = '/Users/Romain/Desktop/gouttelette2.mp4' # '<video0>' for camera
filename = '/Users/Romain/Desktop/Tracking.mp4'
reader = imageio.get_reader(filename)

diameter = 21 # If too large it will be slow
#width = int(cap.get(3))
#height = int(cap.get(4))
#fps = 20.
#print width,height

cv2.namedWindow('Camera', cv2.WINDOW_NORMAL)


    # Capture frame-by-frame
    #ret, frame = cap.read()

for frame in reader:
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #img = frame
    height, width = img.shape[:2]
    img = cv2.resize(img, (int(width / 20), int(height / 20)))  # faster

    f = tp.locate(img, diameter, invert=True, noise_size=1, minmass=1000, max_iterations=1,
                  characterize=True, engine='python')  # numba is too slow!
    xp = np.array(f['x'])
    yp = np.array(f['y'])

    # Closest one
    if len(xp)>0:
        j=np.argmin((xp-width/40)**2+(yp-height/40)**2)
        xt,yt= xp[j],yp[j]
        print len(xp)

    #for i in range(len(xp)):
        #x,y=xp[i]*20,yp[i]*20
        cv2.rectangle(frame,(int(xt*20)-10,int(yt*20)-10),(int(xt*20)+10,int(yt*20)+10),255,1)

    cv2.imshow('track',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    #sleep(0.05)

cv2.destroyAllWindows()
#cap.release()


"""
t1=time()
f = tp.locate(img, diameter, invert=True, noise_size = 2, minmass=100, max_iterations = 1,
              characterize=False, engine = 'python') # numba is too slow!
#f = tp.locate(img, 201, invert=True, minmass=3000, max_iterations=1,
#                            characterize=True, engine = 'python') # numba is too slow!
t2=time()
print(t2-t1)

fig, ax = plt.subplots()
ax.hist(f['mass'], bins=20)
plt.show()
"""