#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import OutputMessageConnector
from ComssServiceDevelopment.service import Service, ServiceController

from ipaddress import *

from Coder.encode import encode
from Coder.decode import decode

import threading

##
## Klasa zarzadzajaca pamiecia aplikacji. Wysyla powiadomienia do GUI o nowych strumieniach i wysyla kolejne pakiety.
## Wymaga, aby GUI posiadalo obsluge:
##    GUI.addStream(id, packetData) - dodawanie nowego strumienia i miniatury
##    GUI.removeStream(id) - usuwanie strumienia i miniatury
##    GUI.nextPacket(id, packetData['body_type'], body) - przeslanie kolejnego pakietu wraz z podaniem typu
##
## Ponadto klasa udostepnia nastepujace metody dla GUI:
##    onGUISetFilter(data) - ustawia filtr dla polaczen
##
class dataManager(object):
    filterOptions = {
        'source_port_start': 6000,
        'source_port_end': 7999,
        'target_port_start': 1000,
        'target_port_end': 80000,
        'source_addres_start': '127.0.0.1',
        'source_addres_end': '127.0.0.1',
        'target_addres_start': '127.0.0.1',
        'target_addres_end': '127.0.0.1',
        'http': True
    }
    storage = {}

    def __init__(self):
        #self.applyFilter()
        pass
        
    def updateFilters(self, values):
        pass

    def setFilterValue(self, data, value):
        newValue = data.get(value, None)
        if not newValue == None:
            if not self.filterOptions[value] == newValue:
                self.filterOptions[value] = newValue
                print "newValue" + str(newValue)
                return True
        return False

    def onGUISetFilter(self, data):
        change = False
        
        if self.setFilterValue(data, 'source_addres_start'):
            change = True
        if self.setFilterValue(data, 'source_addres_end'):
            change = True
        if self.setFilterValue(data, 'source_port_start'):
            change = True
        if self.setFilterValue(data, 'source_port_end'):
            change = True

        if self.setFilterValue(data, 'target_addres_start'):
            change = True

        if self.setFilterValue(data, 'target_addres_end'):
            change = True
        if self.setFilterValue(data, 'target_port_start'):
            change = True
        if self.setFilterValue(data, 'target_port_end'):
            change = True

        #self.setFilterValue(data, 'http')
        
        #print data
        if change:
            self.resetCheck()

    def resetCheck(self):
        print "reset check"
        for id in self.storage:
            self.storage[id] = False
        print self.storage
        
    def between(self, value, name, typ):
        if typ == 'port':
            print "between port value " + str(value) + " | filterOptions: " + str(self.filterOptions.get(name + '_start', 0)) + " - " + str(self.filterOptions.get(name + '_end', 10000000))
            return (value >= self.filterOptions.get(name + '_start', 0)) and (value <= self.filterOptions.get(name + '_end', 10000000))
        elif typ == 'ip':
            print "between ip value " + str(value) + " | filterOptions: " + str(IPv4Address(self.filterOptions.get(name + '_start'))) + " - " +  str(IPv4Address(self.filterOptions.get(name + '_end')))
            return (IPv4Address(value) >= IPv4Address(self.filterOptions.get(name + '_start'))) and (IPv4Address(value) <= IPv4Address(self.filterOptions.get(name + '_end')))
        else:
            return False

    def equals(self, packetData, name):
        return self.filterOptions.get(packetData.get(name, None))

    def checkInFilter(self, packetData):
        print "!!! " + str(packetData)
        return ( self.between(packetData['source']['port'], 'source_port', 'port')  and
          self.between(packetData['target']['port'], 'target_port', 'port') and
          self.between(packetData['source']['address'], 'source_addres', 'ip') and
          self.between(packetData['target']['address'], 'target_addres', 'ip') )#and
          #self.equals(packetData, 'body_type')

    def saveNewPacket(self, packetData, dataManager_stream_output):
        id = self.createId(packetData)
        self.storage[id] = True
        dataManager_stream_output.send(encode({'type': 'id', 'data': packetData}, id))

    def createId(self, packetData):
        return packetData['source']['address'] + str(packetData['source']['port']) + packetData['target']['address'] + str(packetData['target']['port'])

    def checkLocally(self, packetData):
        return not self.storage.get(self.createId(packetData), None) == None

    def GUIRemoveStream(self, id):
        print "GUIRemoveStream " + id
        #GUIRemoveStream(id)

    def notifyGUI(self, packetData, parsedVideoPacket_data, dataManager_stream_output):
        id = self.createId(packetData)
        #GUInextPacket(id, packetData['body_type'], parsedVideoPacket_data)
        
        dataManager_stream_output.send(encode({'type': 'packet', 'id': id, 'body_type': packetData['body_type']}, parsedVideoPacket_data))

    # action to be added in main LOOP of comss
    def receiveData(self, packetData, parsedVideoPacket_data, dataManager_stream_output):
        # if such stream exist
        if self.checkLocally(packetData):
            print "stream exist"
            packet_id = self.createId(packetData)
            
            if self.storage[packet_id] == False: # if not checked
                print "existing stream not checked"
                if not self.checkInFilter(packetData):
                    print "existing check FAILED"
                else:
                    self.storage[packet_id] = True

            else: # check ok
                print "existing stream check ok"
                self.notifyGUI(packetData, parsedVideoPacket_data, dataManager_stream_output)
                #self.storage[packet_id] = True

        else: # new stream
            print "new stream"
            if self.checkInFilter(packetData):
                print "new stream check ok"
                self.saveNewPacket(packetData, dataManager_stream_output)
                self.notifyGUI(packetData, parsedVideoPacket_data, dataManager_stream_output)



class DataManagerService(Service):
    running = 1
    
    def __init__(self):
        Service.__init__(self)
        self.manager = dataManager()
        self.filters_lock = threading.RLock()

    def declare_inputs(self):
        self.declare_input("videoCheckerInput", InputMessageConnector(self))
        self.declare_input("guiInput", InputMessageConnector(self))

    def declare_outputs(self):
        self.declare_output("dataManagerStreamOutput", OutputMessageConnector(self))

    def run(self):	#główna metoda
    
        print "DataManager service started!"
        
        videoChecker_input = self.get_input("videoCheckerInput")
        dataManager_stream_output = self.get_output("dataManagerStreamOutput")

        while self.running == 1:   #pętla główna
            try:
                with self.filters_lock:     #blokada wątku
                    filter_values = {}
                    filter_values['source_port_start'] = int(self.get_parameter("source_port_start"))
                    filter_values['source_port_end']     = int(self.get_parameter("source_port_end"))
                    filter_values['target_port_start']   = int(self.get_parameter("target_port_start"))
                    filter_values['target_port_end']     = int(self.get_parameter("target_port_end"))
                    filter_values['source_addres_start'] = str(self.get_parameter("source_addres_start"))
                    filter_values['source_addres_end']   = str(self.get_parameter("source_addres_end"))
                    filter_values['target_addres_start'] = str(self.get_parameter("target_addres_start"))
                    filter_values['target_addres_end']   = str(self.get_parameter("target_addres_end"))
                    #filter_values['http']                = self.get_parameter("http")
                    #print filter_values
                    self.manager.onGUISetFilter(filter_values)
    
                data = videoChecker_input.read() #obiekt interfejsu
                
                try:
                    packetData = decode(data)
                    #print "DATAMGR packetData size: " + str(len(data))
                    if not packetData == None:
                        self.manager.receiveData(packetData['data'], packetData['body'], dataManager_stream_output)
                except Exception, e:
                    print "some error " + e.message
                    pass
                
            except EOFError:
                print "EOFError"
                pass

if __name__=="__main__":
    sc = ServiceController(DataManagerService, "dataManager_service.json")
    sc.start()
