import cv2

vcap = cv2.VideoCapture("http://31.186.24.232:8000/14")

while(1):

    ret, frame = vcap.read()
    cv2.imshow('VIDEO', frame)
    cv2.waitKey(1)

