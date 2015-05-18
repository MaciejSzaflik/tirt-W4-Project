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
        except IOError, e:
            #print "cannot im = Image.open"
            return False
        except:
            #print "cannot im = Image.open"
            return False

        try:
            im.load()
        except IOError:
            #print "cannot im.load"
            pass
        except:
            #print "cannot im = Image.open"
            return False

        return True

    def anotherCheck(self, imgarray):
        return False        

    def run(self):	#główna metoda
    
        print "VideoChecker service started!"
        
        dataManager_input = self.get_input("dataManagerInput")
        videoCheckerOutput = self.get_output("videoCheckerOutput")

        while self.running == 1:   #pętla główna
            try:
                data = dataManager_input.read() #obiekt interfejsu

                try:
                    #print "received " + str(len(data))
                    packetData = decode(data)
                    #print "VIDEOCHKR packetData size: " + str(len(data))
                    if not packetData == None:
                        imgarray = packetData['body']

                        if self.checkJPG(imgarray):
                            packetData['data']['body_type'] = 'http'
                            packetData['data']['offset'] = 0
                            #print "1"
                            dataToSend = encode(packetData['data'], '')
                            #print "VIDEOCHKR output data size: " + str(len(dataToSend))
                            videoCheckerOutput.send(dataToSend)
                        elif self.checkJPG(imgarray[37:]):
                            packetData['data']['body_type'] = 'http'
                            packetData['data']['offset'] = 37
                            #print "2"
                            dataToSend = encode(packetData['data'], '')
                            #print "VIDEOCHKR output data size: " + str(len(dataToSend))
                            videoCheckerOutput.send(dataToSend)
                        elif self.anotherCheck(imgarray):
                            packetData['data']['body_type'] = False
                            #print "3"
                            dataToSend = encode(packetData['data'], '')
                            #print "VIDEOCHKR output data size: " + str(len(dataToSend))
                            videoCheckerOutput.send(dataToSend)

                except Exception, e:
                    pass

            except EOFError:
                print "EOFError"
                pass
            #except socket.error:
            #    pass
            
                

if __name__=="__main__":
    sc = ServiceController(VideoCheckerService, "videoChecker_service.json")
    sc.start()
