#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import OutputMessageConnector
from ComssServiceDevelopment.service import Service, ServiceController


from ipaddress import *

from Coder.encode import encode
from Coder.decode import decode

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
        'source_addres_start': '127.0.0.1',
        'source_addres_end': '127.0.0.1',
        'target_addres_start': '127.0.0.1',
        'target_addres_end': '127.0.0.1',
        'http': True
    }
    storage = {}

    def __init__(self):
        self.applyFilter()

    def setFilterValue(self, data, value):
        if not data.get(value, None) == None:
            self.filterOptions[value] = data.get(value, None)

    def onGUISetFilter(self, data):
        setFilterValue(data, 'source_addres_start')
        setFilterValue(data, 'source_addres_end')
        setFilterValue(data, 'source_port_start')
        setFilterValue(data, 'source_port_end')

        setFilterValue(data, 'target_addres_start')
        setFilterValue(data, 'target_addres_end')
        setFilterValue(data, 'target_port_start')
        setFilterValue(data, 'target_port_end')
        setFilterValue(data, 'http')

        self.applyFilter()

    def applyFilter(self):
        for id in self.storage:
            if not self.checkInFilter(self.storage[id]):
                self.GUIRemoveStream(id)

    def between(self, value, name, typ):
        if typ == 'port':
            return value >= self.filterOptions.get(name + '_start', 0) and value <= self.filterOptions.get(name + '_end', 10000000)
        elif typ == 'ip':
            return IPv4Address(value) >= IPv4Address(self.filterOptions.get(name + '_start')) and IPv4Address(value) <= IPv4Address(self.filterOptions.get(name + '_end'))
        else:
            return False

    def equals(self, packetData, name):
        return self.filterOptions.get(packetData.get(name, None))

    def checkInFilter(self, packetData):
        return (self.between(packetData['source']['port'], 'source_port', 'port') and
          self.between(packetData['target']['port'], 'target_port', 'port') and
          self.between(packetData['source']['address'], 'source_addres', 'ip') and
          self.between(packetData['target']['address'], 'target_addres', 'ip') and
          self.equals(packetData, 'body_type'))

    def saveNewPacket(self, packetData, dataManager_stream_output):
        id = self.createId(packetData)
        self.storage[id] = 'small'
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
        if self.checkLocally(packetData):
            self.notifyGUI(packetData, parsedVideoPacket_data, dataManager_stream_output)
        else:
            if self.checkInFilter(packetData):
                self.saveNewPacket(packetData, dataManager_stream_output)
                self.notifyGUI(packetData, parsedVideoPacket_data, dataManager_stream_output)



class DataManagerService(Service):
    running = 1
    
    def __init__(self):
        Service.__init__(self)
        self.manager = dataManager()

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
