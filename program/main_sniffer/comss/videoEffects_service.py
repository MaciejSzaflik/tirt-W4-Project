#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import OutputMessageConnector
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector
from ComssServiceDevelopment.service import Service, ServiceController

import socket, sys
from struct import *
import threading

import cv, cv2

import numpy

from cStringIO import StringIO
from PIL import Image, ImageTk

from Coder.encode import encode
from Coder.decode import decode

class VideoEffectsService(Service):
    running = 1
    
    invertedColors = False
    monochrome = False
    blur = False
    
    def __init__(self):
        Service.__init__(self)

        self.filters_lock = threading.RLock()

    def declare_inputs(self):	#deklaracja wejść
        self.declare_input("dataManagerStreamInput", InputMessageConnector(self))
        
    def declare_outputs(self):	#deklaracja wyjść
        self.declare_output("videoEffectsGUIOutput", OutputMessageConnector(self))

    # GŁÓWNA METODA USŁUGI
    def run(self):
        self.dataManager_input = self.get_input("dataManagerStreamInput")
        self.videoEffects_output = self.get_output("videoEffectsGUIOutput")
        print "videoEffects service started."
        while self.running == 1:
            with self.filters_lock:     #blokada wątku
                self.invertedColors = self.get_parameter("invertedColors")
                self.monochrome = self.get_parameter("monochrome")
                self.blur = self.get_parameter("blur")
            self.processVideo()
    
    def processVideo(self):
        data = self.dataManager_input.read()
        packetData = decode(data)
        frame = 0
        im = 0
        
        if not packetData == None:
            #print "received data:"
            #print data
            if packetData['data']['type'] == 'packet':
                if self.invertedColors or self.monochrome or self.blur: #if any filter on
                    imgarray = packetData['body']

                    #print imgarray
                    try:

                        im = Image.open(StringIO(imgarray))
                        im.load()

                    except Exception, e:

                        try:
                            im = Image.open(StringIO(imgarray[37:]))
                            im.load()
                            
                            #print im
                            
                        except Exception, e:
                            pass
                            
                    #print im
                    if not im == 0:
                        
                        try:
                            im = im.convert('RGB')
                            frame = numpy.array(im)
                            # Convert RGB to BGR
                            frame = frame[:, :, ::-1].copy()
                            
                            #apply effects conditionally
                            
                            if self.invertedColors:
                                frame = cv2.bitwise_not(frame)
                            if self.monochrome:
                                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            if self.blur:
                                frame = cv2.blur(frame,(10,10)) 
                            
                            # opencv to jpg bytes
                            img_body = cv2.imencode('.jpg', frame)[1].tostring()
                            packetData['body'] = img_body
                            
                            data = encode(packetData['data'], packetData['body'])

                        except Exception, e:
                            #print "OPENCV LOAD FAIL"
                            #print e
                            #print "\n\n"
                            pass
                            

        self.videoEffects_output.send(data)

if __name__=="__main__":
    sc = ServiceController(VideoEffectsService, "videoEffects_service.json")
    sc.start()
