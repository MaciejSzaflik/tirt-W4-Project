__author__ = 'maciej'
import av
from PIL import Image
import StringIO
import time


class FrameReader(object):
    def __init__(self, pathToFile=""):
        self.pathToFile = pathToFile
        self.container = av.open(pathToFile)
        self.current_milli_time = lambda: int(round(time.time()*3000))
        self.currentTime =  self.current_milli_time()
        self.listOfFrames = []
        self.counter = 0
        for packet in self.container.demux():
            for frame in packet.decode():
                if frame != None:
                    self.listOfFrames.append(self.convertToString(frame))


    def get_frame(self):

        time =  self.current_milli_time()

        if   time - self.currentTime <=1:
            return self.listOfFrames[self.counter]
        else:
            self.currentTime = time
        self.counter+=1
        if self.counter >= len(self.listOfFrames):
            self.counter = 0
            return self.listOfFrames[self.counter]
        else:
            return self.listOfFrames[self.counter]




    def convertToString(self,frame):
        img = frame.to_nd_array()
        im = Image.fromarray(img)
        buf = StringIO.StringIO()
        im.save(buf, format='JPEG')
        jpeg = buf.getvalue()
        return jpeg


