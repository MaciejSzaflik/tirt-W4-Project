#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ComssServiceDevelopment.connectors.udp.multicast import OutputMulticastConnector
from ComssServiceDevelopment.service import Service, ServiceController

import socket, sys
from struct import *
import threading

class myThread (threading.Thread):
    def __init__(self, threadID, name, mainObject):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.mainObject = mainObject
    def run(self):
        print "alfa 0.2 testing"
        while self.mainObject.running == 1:
            self.mainObject.readPacketFromSocket()
            self.mainObject.wire_output.send(self.mainObject.packet)

class WireService(Service):

    TextPacket = 0
    mainSocket = 0
    nextPacket = 0

    nextTCP = 0
    nextUDP = 0

    running = 1

    nextPCK = 0

    def declare_inputs(self):
        pass
        
    def declare_outputs(self):	#deklaracja wyjść
        self.declare_output("wireOutput", OutputMulticastConnector(self))
        self.createSocketConnection()


    # GŁÓWNA METODA USŁUGI
    def run(self):
        self.wire_output = self.get_output("wireOutput")
        print "Wire service started."

    def createSocketConnection(self):
        if self.mainSocket == 0:
            try:
                self.mainSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
            except socket.error, msg:
                print 'Socket could not be created. Error Code: ' + str(msg[0]) + ' Message ' + msg[1]
                sys.exit()
            try:
                thread1 = myThread(1, "alfa", self)
                thread1.start()
            except:
                print "Error: unable to start thread"
        else:
            print("pff")
    
    def readPacketFromSocket(self):
        self.packet = self.mainSocket.recvfrom(16384)#65535)
        self.nextPCK = self.nextPCK + 1

if __name__=="__main__":
    sc = ServiceController(WireService, "wire_service.json")
    sc.start()
