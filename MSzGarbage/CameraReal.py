__author__ = 'maciej'
import cv2
import Image
import StringIO

class CameraReal(object):
    def __init__(self):
         self.cam = cv2.VideoCapture(0)

    def get_frame(self):
        img = self.cam.read()[1]
        im = Image.fromarray(img)

        buf= StringIO.StringIO()
        im.save(buf, format= 'JPEG')
        jpeg= buf.getvalue()
        return jpeg