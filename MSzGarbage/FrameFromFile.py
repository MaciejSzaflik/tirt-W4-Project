__author__ = 'maciej'
import av
from PIL import Image
import StringIO


class FrameReader(object):
    def __init__(self, pathToFile=""):
        self.pathToFile = pathToFile
        self.container = av.open(pathToFile).demux()


    def get_frame(self):
        try:
            frames = self.container.next().decode()
        except:
            self.container = av.open(self.pathToFile).demux()
            frames = self.container.next().decode()

        for frame in frames:
            if frame != None:
                img = frame.to_nd_array()
                im = Image.fromarray(img)
                buf = StringIO.StringIO()
                im.save(buf, format='JPEG')
                jpeg = buf.getvalue()
                return jpeg



