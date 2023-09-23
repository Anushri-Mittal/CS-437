import time
import datetime

import numpy as np
import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput
from libcamera import controls

import socket

message = "Motion Detected!"
ip_addr = "10.192.226.197"
port_num = 5000


import cv2
picam2=Picamera2()  ## Create a camera object
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP



dispW=1280
dispH=720
## Next, we configure the preview window size that determines how big should the image be from the camera, the bigger the image the more the details you capture but the slower it runs
## the smaller the size, the faster it can run and get more frames per second but the resolution will be lower. We keep 
picam2.preview_configuration.main.size= (dispW,dispH)  ## 1280 cols, 720 rows. Can also try smaller size of frame as (640,360) and the largest (1920,1080)
## with size (1280,720) you can get 30 frames per second

## since OpenCV requires RGB configuration we set the same format for picam2. The 888 implies # of bits on Red, Green and Blue
picam2.preview_configuration.main.format= "RGB888"
picam2.preview_configuration.align() ## aligns the size to the closest standard format
picam2.preview_configuration.controls.FrameRate=30 ## set the number of frames per second, this is set as a request, the actual time it takes for processing each frame and rendering a frame can be different

picam2.configure("preview")
## 3 types of configurations are possible: preview is for grabbing frames from picamera and showing them, video is for grabbing frames and recording and images for capturing still images.

picam2.start()
## Number of previous frames to update background model
num_history_frames=15
## Gets the background subtractor object
back_sub= cv2.createBackgroundSubtractorMOG2(history=num_history_frames, \
varThreshold=75, \
detectShadows=False)
time.sleep(0.1)
max_foreground=200 # (0-255)

kernel= np.ones((20,20), np.uint8)

faceCascade=cv2.CascadeClassifier("/home/pi/Downloads/haarcascade_frontalface_default.xml")
bodyCascade=cv2.CascadeClassifier("/home/pi/Downloads/haarcascade_fullbody.xml")

while True:
    #tstart=time.time()
    
    frame=picam2.capture_array() ## frame is a large 2D array of rows and cols and at intersection of each point there is an array of three numbers for RGB i.e. [R,G,B] where RGB value ranges from 0 to 255
    
   
    fgmask = back_sub.apply(frame) ## obtains the foreground mask
    
    fgmask=cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, kernel)
    fgmask=cv2.medianBlur(fgmask,5)
    
    _,fgmask=cv2.threshold(fgmask, max_foreground, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(fgmask, cv2.RETR_TREE, \
    cv2.CHAIN_APPROX_SIMPLE)[-2:]
    areas=[cv2.contourArea(c) for c in contours]
    # if there are no contours
    if len(areas) <1:
        cv2.imshow('Frame', frame)
        key=cv2.waitKey(1) & 0xFF ## wait for key press for 1 millisecond
        if key == ord("q"): ## stops for 1 ms to check if key Q is pressed
            break
        # go to the top of the for loop
        continue
    else: # goes with "if len(areas)<1"
        # find the largest moving object in the frame
        max_index= np.argmax(areas)
    ## Draw the bounding box
    cnt=contours[max_index]
    x,y,w,h= cv2.boundingRect(cnt)
    cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 3)
    
    frameGray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    faces=faceCascade.detectMultiScale(frameGray,1.3,5)
    bodies=bodyCascade.detectMultiScale(frameGray,1.3,5)
    
    # send alert via UDP
    if (len(faces) >= 1) or (len(bodies) >= 1):
        sock.sendto(bytes(message, "utf-8"), (ip_addr, port_num))
    
    # Draw the circle in the center of the bounding box
    x2= x + int(w/2)
    y2= y + int(h/2)
    cv2.circle(frame,(x2,y2), 4, (0,255,0), -1)
    ## Print the centroid coordinates (we'll use the center of the bounding
    ## box) on the image
    text= "x: " + str(x2) + ", y: " + str(y2)
    cv2.putText(frame, text, (x2-10, y2-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
    (0,255,0), 2)
    ## Display the resulting frame
    cv2.imshow("Frame", frame)
    key=cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break


    
    ## frame[rows,columns] --> is the pixel of each frame
    
    ## the above command will only grab the frame
    
    cv2.imshow("piCamera2", frame) ## show the frame
    key=cv2.waitKey(1) & 0xFF
    
    if key ==ord(" "):
        cv2.imwrite("frame-" + str(time.strftime("%H:%M:%S", time.localtime())) + ".jpg", frame)
    if key == ord("q"): ## stops for 1 ms to check if key Q is pressed
        break
    
    #tend= time.time()
    #looptime=tend-tstart
    #fps= 1/looptime ## this is the actual frames per second
    #print("frames per second are",int(fps)) ## if you increase the resolution of the image the fps will go down
    
cv2.destroyAllWindows()