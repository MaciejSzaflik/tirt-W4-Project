#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputStreamConnector
from ComssServiceDevelopment.connectors.udp.multicast import OutputMulticastConnector
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
        self.declare_output("videoCheckerOutput", OutputMulticastConnector(self))
        #self.createSocketConnection()
        
    def createSocketConnection(self):
        if self.mainSocket == 0:
            try:
                self.mainSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
            except socket.error, msg:
                print 'Socket could not be created. Error Code: ' + str(msg[0]) + ' Message ' + msg[1]
                sys.exit()
            #try:
                #thread1 = myThread(1, "alfa", self)
                #thread1.start()
            #except:
            #    print "Error: unable to start thread"
        else:
            print("pff")
        
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
                elif self.checkJPG(imgarray[37:]):
                    #wire_input['data']['body_type'] = 'jpg'
                    #manage(data, wire_input['body'][37:], id, object)
                    print "2"
                elif self.anotherCheck(imgarray):
                    #wire_input['data']['body_type'] = 'never accessed here'
                    #manage(data, imgarray, id, object)
                    print "3"
            except EOFError:
                print "EOFError"
                pass
            #except socket.error:
            #    pass
            
                

if __name__=="__main__":
    sc = ServiceController(VideoCheckerService, "videoChecker_service.json")
    sc.start()
