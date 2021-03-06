__author__ = 'maciej'
import cv2
from PIL import Image
import StringIO


class CameraReal(object):
    def __init__(self, fromFile=False, pathToFile=""):
        self.fromFile = fromFile
        self.pathToFile = pathToFile
        if self.fromFile:
            self.videoFile = cv2.VideoCapture(pathToFile)
            while not self.videoFile.isOpened():
                self.videoFile = cv2.VideoCapture(pathToFile)
                cv2.waitKey(1000)
                print "Wait for the header file"
        else:
            self.cam = cv2.VideoCapture(0)
            while not self.cam.isOpened():
                self.cam = cv2.VideoCapture(0)
                cv2.waitKey(1000)
                print "Wait for the header video"

    def get_frame(self):
        if self.fromFile:
            flag, img = self.videoFile.read()
            if flag == 0:
                self.videoFile.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,0)
                _,img= self.videoFile.read()
        else :
            _,img = self.cam.read()[1]

        im = Image.fromarray(img)
        buf = StringIO.StringIO()
        im.save(buf, format='JPEG')
        jpeg = buf.getvalue()
        self.lastImage = jpeg
        return jpeg
