__author__ = 'maciej'
__editor__ = 'michalvvv'

#!/usr/bin/env python
import sys
from flask import Flask, render_template, Response
from CameraReal import CameraReal
from FrameFromFile import FrameReader


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame!=None:
            yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(FrameReader('drift.mp4')),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def num(s):
    try:
        return int(s[1])
    except:
        return 5000

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=num(sys.argv))
