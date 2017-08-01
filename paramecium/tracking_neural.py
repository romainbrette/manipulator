'''
Tracking with a convolutional neural network
'''
import numpy as np
import cv2
from keras.models import load_model
from AutomaticPatch.Camera import *

cam = Camera('Hamamatsu', None)
model_name = 'seq_2d_50.h5'
subFrameSize = 75
FPS = 20
model = load_model(model_name)

previous = None

while True:
    frame = cam.frame

    if frame is None:
        continue

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #img = frame
    img = cv2.resize(img, (subFrameSize, subFrameSize))
    #img = img[135-subFrameSize/2:135+subFrameSize/2+1,316-subFrameSize/2:316+subFrameSize/2+1]

    img = img.astype(np.float32)
    img = img / 255

    # Normalize
    #img = img-img.min()
    #img = img/img.max()

    if previous is None:
        previous = img
        continue

    nn_input = np.array([[previous, img]], dtype=np.float32)
    #nn_input = np.array([[img, img]], dtype=np.float32) # we don't use the previous image; doesn't work

    previous = img

    # make predictions
    out = model.predict(nn_input)
    out = out * subFrameSize/2 # not normalized!??
    predict_X, predict_Y = out[0,0], out[0,1]

    # print image
    frame = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    posX, posY = int(predict_X + subFrameSize/2), int(predict_Y + subFrameSize/2)
    cv2.circle(frame, (posX, posY), 5, (0,255,0), 1)
    # print("%.2f %.2f" % (predict_X, predict_Y))
    print predict_X,predict_Y

    cv2.imshow('track',cv2.resize(frame,(200,200)))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
