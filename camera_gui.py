'''
Camera window.
Requires Opencv.
Quit with key 'q'

Note: my infinity camera has variable resolution, but
it seems that OpenCV sets it to 640x480 by default (maybe could be set)
'''
import cv2

#from os.path import expanduser
#home = expanduser("~")
#filename = home+'/video.avi'

#def click(event, x, y, flags, param):
#    if event == cv2.EVENT_LBUTTONDOWN:
#        print x,y
#
cap = cv2.VideoCapture(0)
#cap.set(3, 640)
#cap.set(4, 480)

width = int(cap.get(3))
height = int(cap.get(4))
#fps = 20.
#print width,height,fps

cv2.namedWindow('Camera')
#cv2.setMouseCallback("Camera", click)

#fourcc = cv2.cv.CV_FOURCC(*'mp4v') # on mac
#fourcc = cv2.cv.CV_FOURCC(*'DIVX')
#fourcc = -1 # On Windows
#video = cv2.VideoWriter(filename,fourcc,fps,(width,height), True)

#save = False

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    width, height, _ = frame.shape

    # Our operations on the frame come here

    #if save:
    #    video.write(frame)

    cv2.line(frame, (height/2, width/2-10), (height/2, width/2+10), (0, 0, 255))
    cv2.line(frame, (height/2-10, width/2), (height/2+10, width/2), (0, 0, 255))
    #frame = cv2.flip(frame, 1)

    # Display the resulting frame
    cv2.imshow('Camera',frame)

    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break
    #if key & 0xFF == ord('s'):
    #    save = not save
    #    print "Save =",save

# When everything done, release the capture
cap.release()
#video.release()
cv2.destroyAllWindows()
