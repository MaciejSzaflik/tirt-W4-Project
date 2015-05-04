#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputStreamConnector
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import OutputStreamConnector
from ComssServiceDevelopment.service import Service, ServiceController
import socket, sys
import time

from Tkinter import *
import Tkinter as Tk
from PIL import Image, ImageTk

from cStringIO import StringIO

class VideoCheckerService(Service):

    mainSocket = 0
    running = 1

    def declare_inputs(self):
        self.declare_input("wireInput", InputStreamConnector(self))
        
    def declare_outputs(self):
        self.declare_output("videoCheckerOutput", OutputStreamConnector(self))
        
    def checkJPG(self, imgarray):
        try:
            im = Image.open(StringIO(imgarray))
        except IOError:
            #print "cannot im = Image.open"
            return False

        try:
            im.load()
        except IOError:
            #print "cannot im.load"
            pass

        return True

    def anotherCheck(self, imgarray):
        return False        

    def run(self):	#główna metoda
    
        print "VideoChecker service started!"
        
        wire_input = self.get_input("wireInput")
        videoCheckerOutput = self.get_output("videoCheckerOutput")

        while self.running == 1:   #pętla główna
            try:
                imgarray = wire_input.read() #obiekt interfejsu 
                #if wire_input['body']:
                #print "\n\n"
                #print imgarray

                if self.checkJPG(imgarray):
                    #wire_input['data']['body_type'] = 'jpg'
                    #manage(data, wire_input['body'], id, object)
                    print "1"
                    videoCheckerOutput.send(imgarray)
                elif self.checkJPG(imgarray[37:]):
                    #wire_input['data']['body_type'] = 'jpg'
                    #manage(data, wire_input['body'][37:], id, object)
                    print "2"
                    videoCheckerOutput.send(imgarray)
                elif self.anotherCheck(imgarray):
                    #wire_input['data']['body_type'] = 'never accessed here'
                    #manage(data, imgarray, id, object)
                    print "3"
                    videoCheckerOutput.send(imgarray)
            except EOFError:
                print "EOFError"
                pass
            #except socket.error:
            #    pass
            
                

if __name__=="__main__":
    sc = ServiceController(VideoCheckerService, "videoChecker_service.json")
    sc.start()
