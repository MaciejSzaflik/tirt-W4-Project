#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import OutputMessageConnector
from ComssServiceDevelopment.service import Service, ServiceController

import socket, sys
from struct import *
import threading

from cStringIO import StringIO
from PIL import Image, ImageTk

from Coder.encode import encode

class WireService(Service):
    mainSocket = 0
    running = 1

    def declare_inputs(self):	#deklaracja wejść
        pass
        
    def declare_outputs(self):	#deklaracja wyjść
        self.declare_output("wireOutput", OutputMessageConnector(self))
        self.createSocketConnection()

    # GŁÓWNA METODA USŁUGI
    def run(self):
        self.wire_output = self.get_output("wireOutput")
        print "Wire service started."
        while self.running == 1:
            self.readPacketFromSocket()

    def createSocketConnection(self):
        if self.mainSocket == 0:
            try:
                self.mainSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
                print "running v0.3"
            except socket.error, msg:
                print 'Socket could not be created. Error Code: ' + str(msg[0]) + ' Message ' + msg[1]
                sys.exit()
        else:
            print("pff")
    
    def readPacketFromSocket(self):
        packet = self.mainSocket.recvfrom(65535)
        packetData = self.decipherWhatIsInside(packet)
        if packetData and packetData['data'] and (packetData['data']['source']['port'] < 10070 or packetData['data']['source']['port'] > 10081) and (packetData['data']['target']['port'] < 10070 or packetData['data']['target']['port'] > 10081):
            #try:
            #    f = open('wire.jpg', 'w')
            #    f.write(packetData['body'][37:])
            #    f.close()
            #except IOError, e:
            #    print e.message
            dataToSend = encode(packetData['data'], packetData['body'])
            #print "WIRE output data size: " + str(len(dataToSend))
            self.wire_output.send(dataToSend)

    def decipherWhatIsInside(self, packet):
        #parse ethernet header
        packet = packet[0]
        eth_length = 14

        eth_header = packet[:eth_length]
        eth = unpack('!6s6sH' , eth_header)
        eth_protocol = socket.ntohs(eth[2])

        #Parse IP packets, IP Protocol number = 8
        if eth_protocol == 8 :
            #Parse IP header
            #take first 20 characters for the ip header
            ip_header = packet[eth_length:20+eth_length]

            #now unpack them :)
            iph = unpack('!BBHHHBBH4s4s' , ip_header)

            version_ihl = iph[0]
            version = version_ihl >> 4
            ihl = version_ihl & 0xF

            iph_length = ihl * 4

            ttl = iph[5]
            protocol = iph[6]
            s_addr = socket.inet_ntoa(iph[8]);
            d_addr = socket.inet_ntoa(iph[9]);
            if protocol == 6 :
                t = iph_length + eth_length
                tcp_header = packet[t:t+20]

                tcph = unpack('!HHLLBBHHH' , tcp_header)

                source_port = tcph[0]
                dest_port = tcph[1]
                sequence = tcph[2]
                acknowledgement = tcph[3]
                doff_reserved = tcph[4]
                tcph_length = doff_reserved >> 4

                h_size = eth_length + iph_length + tcph_length * 4

                #get data from the packet
                body = packet[h_size:]

                data = {}
                data['eth_protocol'] = eth_protocol
                data['version'] = version
                data['ihl'] = ihl
                data['source'] = {}
                data['source']['address'] = s_addr
                data['source']['port'] = source_port
                data['target'] = {}
                data['target']['address'] = d_addr
                data['target']['port'] = dest_port
                data['sequence'] = sequence
                data['acknowledgement'] = acknowledgement
                data['doff_reserved'] = doff_reserved
                data['tcph_length'] = tcph_length
                data['h_size'] = h_size

                packetData = {}
                packetData['data'] = data
                packetData['body'] = body
                return packetData

if __name__=="__main__":
    sc = ServiceController(WireService, "wire_service.json")
    sc.start()
