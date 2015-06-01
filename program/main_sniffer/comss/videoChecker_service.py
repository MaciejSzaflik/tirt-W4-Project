#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import OutputMessageConnector
from ComssServiceDevelopment.service import Service, ServiceController
import socket, sys
import time

from Tkinter import *
import Tkinter as Tk
from PIL import Image, ImageTk

from cStringIO import StringIO

from Coder.encode import encode
from Coder.decode import decode

class VideoCheckerService(Service):
    mainSocket = 0
    running = 1

    def declare_inputs(self):
        self.declare_input("dataManagerInput", InputMessageConnector(self))
        
    def declare_outputs(self):
        self.declare_output("videoCheckerOutput", OutputMessageConnector(self))
        
    def checkJPG(self, imgarray):
        try:
            im = Image.open(StringIO(imgarray))
        except:
            return False

        try:
            im.load()
        except:
            return False

        return True

    def run(self): #główna metoda
        print "VideoChecker service started!"

        dataManager_input = self.get_input("dataManagerInput")
        videoCheckerOutput = self.get_output("videoCheckerOutput")

        while self.running == 1:   #pętla główna
            try:
                data = dataManager_input.read() #obiekt interfejsu

                try:
                    packetData = decode(data)
                    try:
                        if not packetData == None:
                            imgarray = packetData['body']

                            if self.checkJPG(imgarray):
                                packetData['data']['body_type'] = 'http'
                                packetData['data']['offset'] = 0
                                dataToSend = encode(packetData['data'])
                                videoCheckerOutput.send(dataToSend)
                            elif self.checkJPG(imgarray[37:]):
                                packetData['data']['body_type'] = 'http'
                                packetData['data']['offset'] = 37
                                dataToSend = encode(packetData['data'])
                                videoCheckerOutput.send(dataToSend)
                            else:
                                packetData['data']['body_type'] = False
                                dataToSend = encode(packetData['data'])
                                videoCheckerOutput.send(dataToSend)
                    except Exception, e1:
                        print e1.message
                        try:
                            packetData['data']['body_type'] = False
                            print 'NOT by exc'
                            dataToSend = encode(packetData['data'])
                            videoCheckerOutput.send(dataToSend)
                        except Exception, e2:
                            print e2.message
                            pass
                except Exception, e3:
                    print e3.message
                    pass

            except Exception, e4:
                print e4.message
                pass

if __name__=="__main__":
    sc = ServiceController(VideoCheckerService, "videoChecker_service.json")
    sc.start()

