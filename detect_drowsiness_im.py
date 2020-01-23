from scipy.spatial import distance as dist
#from imutils.video import VideoStream
from imutils.video import WebcamVideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import playsound
import argparse
import imutils
import time
import dlib
import cv2

from socket import *

HOST = '127.0.0.1'
#HOST = '27.96.130.164'
#HOST = '192.168.0.11'
PORT = 1117
BUFSIZE = 1024
ADDR = (HOST,PORT)

client_socket = socket(AF_INET, SOCK_STREAM)

try:
    client_socket.connect(ADDR)
    print('client connection is success..')
    


except Exception as e:
    print('connection error %s:%s'%ADDR)
    



def sound_alarm(path):
    # play an alarm sound
    playsound.playsound("./alarm.wav")
    #playsound.playsound("/home/pi/cty/Drowsiness-detection/alarm.wav")
def sending(data):
    message = 'Alert(DWS)'
    message = message.encode('utf-8')
    client_socket.send(message)    


def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])

    ear = (A + B) / (2.0 * C)

    return ear


ap = argparse.ArgumentParser()
ap.add_argument('-p', "--shape-predictor", required = True,
    help = "path to facial landmark predictor")
ap.add_argument('-a', "--alarm", type = str, default = "",
    help = "path to alarm .wav file")
ap.add_argument('-w', "--webcam", type = str, default = 0,
    help = "index of webcam on system")
args = vars(ap.parse_args())


EYE_AR_THRESH = 0.23
EYE_AR_CONSEC_FRAMES = 48

COUNTER = 0
ALARM_ON = False


print("[INFO] Loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(args["shape_predictor"])

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]


print("[INFO] Starting video stream thread...")
cam = WebcamVideoStream(src=0).start()
#cam = cv2.VideoCapture(0) #d
#cam.set(3, 320) #d
#cam.set(4, 240) #d

time.sleep(1.0)


# loop over frames from the video stream
while True:
    frame = cam.read()
    frame = imutils.resize(frame, width = 400)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    rects = detector(gray, 0)

    # loop over the face detections
    for rect in rects:
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        leftEye = shape[lStart:lEnd] #
        rightEye = shape[rStart:rEnd] #
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)

        ear = (leftEAR + rightEAR) / 2.0

        leftEyeHull = cv2.convexHull(leftEye) #
        rightEyeHull = cv2.convexHull(rightEye) #
        cv2.drawContours(frame, [leftEyeHull], -1, (66, 244, 197), 1) #
        cv2.drawContours(frame, [rightEyeHull], -1, (66, 244, 197), 1) #

        if ear < EYE_AR_THRESH:
            COUNTER += 1

            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                if not ALARM_ON:
                    ALARM_ON = True

                    if args["alarm"] != "":
                        t = Thread(target=sound_alarm,
                            args=(args["alarm"],))
                        t.daemon = True
                        t.start()
                                       
                        th = Thread(target=sending,
                            args=(args["alarm"],))
                        th.daemon = True
                        th.start()

                cv2.putText(frame, "Drowsing!!", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            '''
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                message = 'Alert(DWS)'                
                th = Thread(target=sending(message.encode('utf-8'),args=())
                th.daemon = True
                th.start()
            '''
        else:
            COUNTER = 0
            ALARM_ON = False

        cv2.putText(frame, "EAR: {:.2f}".format(ear), (150, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    '''    
    getdata = client_socket.recv(BUFSIZE)
    if getdata.decode('utf-8') == 'Webcam OFF':
        cam.stop()
    elif getdata.decode('utf-8') == 'Webcam ON':
        cam.read()
    '''
    

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
print('closing...')
cv2.destroyAllWindows()
cam.stop()
