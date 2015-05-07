#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputStreamConnector
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import OutputStreamConnector
from ComssServiceDevelopment.service import Service, ServiceController


from Coder.encode import encode
from Coder.decode import decode
    

##
## Klasa zarzadzajaca pamiecia aplikacji. Wysyla powiadomienia do GUI o nowych strumieniach i wysyla kolejne pakiety.
## Wymaga, aby GUI posiadalo obsluge:
##    GUI.addStream(key, packetData) - dodawanie nowego strumienia i miniatury
##    GUI.removeStream(key) - usuwanie strumienia i miniatury
##    GUI.nextPacket(key, packetData['body_type'], body) - przeslanie kolejnego pakietu wraz z podaniem typu
##
## Ponadto klasa udostepnia nastepujace metody dla GUI:
##    onGUISetFilter(data) - ustawia filtr dla polaczen
##    onGUISelectStream(key) - zmiana rozmiaru wysylanego strumienia na wiekszy
##    onGUIUnselectStream(key) - zmiana rozmiaru wysylanego strumienia na mniejszy
##    onGUISetSize(size, width, height) - zmiana rozdzielczosci wyswietlania
##
class dataManager(object):
    filterOptions = {
        'source_port_start': 6000,
        'source_port_end': 7999,
        'http': True
    }
    storage = {}
    sizeOptions = {
        'small': {
            'width': 300,
            'height': 200
        },
        'big': {
            'width': 1000,
            'height': 800
        }
    }
    lastSelected = None

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
        for key in self.storage:
            if not self.checkInFilter(self.storage[key]):
                self.GUIRemoveStream(key)

    def between(self, value, name):
        return value >= self.filterOptions.get(name + '_start', 0) and value <= self.filterOptions.get(name + '_end', 10000000)

    def equals(self, packetData, name):
        return self.filterOptions.get(packetData.get(name, None))

    def checkInFilter(self, packetData):
        return (self.between(packetData['source']['port'], 'source_port') and
          self.between(packetData['target']['port'], 'target_port') and
          #self.between(packetData['source']['address'], 'source_addres') and
          #self.between(packetData['target']['address'], 'target_addres') and
          self.equals(packetData, 'body_type'))

    def saveNewPacket(self, packetData, dataManager_stream_output):
        key = self.createKey(packetData)
        self.storage[key] = 'small'
        dataManager_stream_output.send(encode({'type': 'key', 'data': packetData}, key))

    def createKey(self, packetData):
        return packetData['source']['address'] + str(packetData['source']['port']) + packetData['target']['address'] + str(packetData['target']['port'])

    def checkLocally(self, packetData):
        return not self.storage.get(self.createKey(packetData), None) == None

    def onGUISelectStream(self, key):
        if not self.lastSelected == None:
            self.storage[self.lastSelected] = 'small'
        self.storage[key] = 'big'
        lastSelected = key

    def onGUIUnselectStream(self, key):
        self.storage[key] = 'small'

    def onGUISetSize(self, size, width, height):
        self.sizeOptions[size] = {
            'width': width,
            'height': height
        }

    def GUIRemoveStream(self, key):
        print "GUIRemoveStream " + key
        #GUIRemoveStream(key)

    def notifyGUI(self, packetData, parsedVideoPacket_data, dataManager_stream_output):
        key = self.createKey(packetData)
        #GUInextPacket(key, packetData['body_type'], parsedVideoPacket_data)
        dataManager_stream_output.send(encode({'type': 'packet', 'key': key}, parsedVideoPacket_data))

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
        self.declare_input("videoCheckerInput", InputStreamConnector(self))
        self.declare_input("guiInput", InputStreamConnector(self))

    def declare_outputs(self):
        self.declare_output("dataManagerStreamOutput", OutputStreamConnector(self))

    def run(self):	#główna metoda
    
        print "DataManager service started!"
        
        videoChecker_input = self.get_input("videoCheckerInput")
        dataManager_stream_output = self.get_output("dataManagerStreamOutput")

        while self.running == 1:   #pętla główna
            try:
                data = videoChecker_input.read() #obiekt interfejsu
                #print data
                
                try:
                    packetData = decode(data)
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
