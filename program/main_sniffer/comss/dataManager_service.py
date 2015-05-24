#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import OutputMessageConnector
from ComssServiceDevelopment.service import Service, ServiceController

from ipaddress import *

from Coder.encode import encode
from Coder.decode import decode

import threading

import signal

from datetime import datetime

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

    lastBigId = None

    # types in storage['state']:
    # None - nothing
    # True - is being verified in videoChecker
    # False - negatively verified in videoChecker
    # string - stream type
    # types in storage['filter']:
    # True - accepted by filter
    # False - not accepted by filter
    storage = {}

    def __init__(self, service):
        self.service = service
        #self.applyFilter()

        self.removeOldElementsInterval()
        pass
        
    def updateFilters(self, values):
        pass
        
    def setdataManagerVideoEffectsOutput(self, output):
        self.dataManager_gui_output = output

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
       # print "reset check"
        for id in self.storage:
            self.storage[id]['filter'] = self.checkInFilter(self.storage[id])
            if not self.storage[id]['filter']:
                self.GUIRemoveStream(id)
       # print self.storage
        
    def between(self, value, name, typ):
        if typ == 'port':
        #    print "between port value " + str(value) + " | filterOptions: " + str(self.filterOptions.get(name + '_start', 0)) + " - " + str(self.filterOptions.get(name + '_end', 10000000))
            return (value >= self.filterOptions.get(name + '_start', 0)) and (value <= self.filterOptions.get(name + '_end', 10000000))
        elif typ == 'ip':
      #      print "between ip value " + str(value) + " | filterOptions: " + str(IPv4Address(self.filterOptions.get(name + '_start'))) + " - " +  str(IPv4Address(self.filterOptions.get(name + '_end')))
            return (IPv4Address(value) >= IPv4Address(self.filterOptions.get(name + '_start'))) and (IPv4Address(value) <= IPv4Address(self.filterOptions.get(name + '_end')))
        else:
            return False

    def equals(self, packetData, name):
        return self.filterOptions.get(packetData.get(name, None))

    def checkInFilter(self, packetData):
       # print "!!! " + str(packetData)
        return ( self.between(packetData['source']['port'], 'source_port', 'port')  and
          self.between(packetData['target']['port'], 'target_port', 'port') and
          self.between(packetData['source']['address'], 'source_addres', 'ip') and
          self.between(packetData['target']['address'], 'target_addres', 'ip') )#and
          #self.equals(packetData, 'body_type')

    def saveNewPacket(self, id, packetData, dataManager_gui_output):
        dataManager_gui_output.send(encode({'type': 'id', 'data': packetData}, id))

    def createId(self, packetData):
        return packetData['source']['address'] + str(packetData['source']['port']) + packetData['target']['address'] + str(packetData['target']['port'])


    def removeOldElementsInterval(self):
        if self.service.running == 1:
            threading.Timer(10.0, self.removeOldElementsInterval).start()
            #print "interval"
            
            toRemove = {}
            
            for id in self.storage:
                #print str(id) + ' ' + str(self.storage[id]) + ' ' + str(datetime.now())

                if isinstance(self.storage[id].get('state', None), basestring):
                    #print "TAK"
                    prev = self.storage[id].get('time', None)
                    now = datetime.now()
                    if not prev == None:
                        #print str(int((now - prev).total_seconds() * 1000)) + ' ' + str(int((now - prev).total_seconds() * 1000) > 15000)
                        if int((now - prev).total_seconds() * 1000) > 15000:
                            #print "REMOVE"
                            self.GUIRemoveStream(id)
                            toRemove[id] = True

            for id in toRemove:
                del self.storage[id]

    def GUIRemoveStream(self, id):
        #print "GUIRemoveStream " + id
        self.dataManager_gui_output.send(encode({'type': 'remove'}, id))

    def notifyGUI(self, id, body_type, parsedVideoPacket_data, dataManager_gui_output):
        size = self.storage[id].get('size', 'small')
        if size == 'small':
            if int((datetime.now() - self.storage[id].get('time', datetime.now())).total_seconds() * 1000) > 2000:
                dataManager_gui_output.send(encode({'type': 'packet', 'id': id, 'body_type': body_type, 'size': size}, parsedVideoPacket_data))
                self.storage[id]['time'] = datetime.now()
        else:
            dataManager_gui_output.send(encode({'type': 'packet', 'id': id, 'body_type': body_type, 'size': size}, parsedVideoPacket_data))
            self.storage[id]['time'] = datetime.now()



    def handleWire(self, packetData, parsedVideoPacket_data, dataManager_videoChecker_output, dataManager_gui_output):
        id = self.createId(packetData)
        
        #print "id " + id

        value = self.storage.get(id, None)
        #print "value " + str(value)
        if value == None:
            #print "val non"
            self.storage[id] = {}
            #print "saved?"
            if self.checkInFilter(packetData):
                #print "checked + in filter"
                self.storage[id]['filter'] = True
                self.storage[id]['packet'] = packetData
                dataManager_videoChecker_output.send(encode({'id': id}, parsedVideoPacket_data))
            else:
                #print "checked - in filter"
                self.storage[id]['filter'] = False
        elif self.storage[id]['filter'] == True:
            #print "state " + value['state'] + " " + str(isinstance(value['state'], str)) + " " + str(isinstance(value['state'], basestring))
            if isinstance(value['state'], basestring):
                #print "notifyGUI"
                self.notifyGUI(id, value['state'], parsedVideoPacket_data[value['offset']:], dataManager_gui_output)
            #elif value['state'] == True: # is being checked in videoChecker
            #elif value['state'] == False: # negatively verified in videoChecker
        elif self.checkInFilter(packetData['data']):
            self.storage[id]['filter'] == True
            self.storage[id]['packet'] = packetData
            dataManager_videoChecker_output.send(encode({'id': id}, parsedVideoPacket_data))

    def handleVideoChecker(self, packetData, dataManager_gui_output):
        id = packetData['id']

        #print "id in vch " + id
        #print "contents " + str(self.storage[id])

        if self.storage[id]['filter'] == True: # if was waiting for check
            self.storage[id]['state'] = packetData['body_type']
            self.storage[id]['offset'] = packetData['offset']

            self.saveNewPacket(id, self.storage[id]['packet'], dataManager_gui_output)
            self.storage[id]['packet'] = None

    # action to be added in main LOOP of comss
    def receiveWire(self, packetData, parsedVideoPacket_data, dataManager_videoChecker_output, dataManager_gui_output):
        self.handleWire(packetData, parsedVideoPacket_data, dataManager_videoChecker_output, dataManager_gui_output)

    # action to be added in main LOOP of comss
    def receiveVideoChecker(self, packetData, dataManager_gui_output):
        self.handleVideoChecker(packetData, dataManager_gui_output)

    def setBigImage(self, id):
        if not self.storage.get(id, None) == None:
            if not self.lastBigId == None:
                self.storage[self.lastBigId]['size'] = 'small'
            self.lastBigId = id

            self.storage[id]['size'] = 'big'


class WireThread(threading.Thread):
     def __init__(self, service, manager):
         super(WireThread, self).__init__()
         self.service = service
         self.manager = manager

     def run(self):
        print "DataManager::wireInputThread started!"
        wire_input = self.service.get_input("wireInput")
        dataManager_videoChecker_output = self.service.get_output("dataManagerVideoCheckerOutput")
        dataManager_gui_output = self.service.get_output("dataManagerVideoEffectsOutput")

        while self.service.running == 1:   #pętla główna
            try:
                with self.service.filters_lock:     #blokada wątku
                    filter_values = {}
                    filter_values['source_port_start'] = int(self.service.get_parameter("source_port_start"))
                    filter_values['source_port_end']     = int(self.service.get_parameter("source_port_end"))
                    filter_values['target_port_start']   = int(self.service.get_parameter("target_port_start"))
                    filter_values['target_port_end']     = int(self.service.get_parameter("target_port_end"))
                    filter_values['source_addres_start'] = str(self.service.get_parameter("source_addres_start"))
                    filter_values['source_addres_end']   = str(self.service.get_parameter("source_addres_end"))
                    filter_values['target_addres_start'] = str(self.service.get_parameter("target_addres_start"))
                    filter_values['target_addres_end']   = str(self.service.get_parameter("target_addres_end"))
                    #filter_values['http']                = self.service.get_parameter("http")
                    #print filter_values
                    self.manager.onGUISetFilter(filter_values)
    
                data = wire_input.read() #obiekt interfejsu
                
                if len(data) > 800:
                    #print "received from wire " + str(len(data))
                    try:
                        packetData = decode(data)
                        #print "DATAMGR packetData size: " + str(len(data))
                        if not packetData == None:
                            self.manager.receiveWire(packetData['data'], packetData['body'], dataManager_videoChecker_output, dataManager_gui_output)
                    except Exception, e:
                    #    print "some error " + e.message
                        pass
                
            except EOFError:
              #  print "EOFError"
                pass

class VideoCheckerThread(threading.Thread):
    def __init__(self, service, manager):
         super(VideoCheckerThread, self).__init__()
         self.service = service
         self.manager = manager

    def run(self):
        print "DataManager::videoCheckerInputThread started!"
        videoChecker_input = self.service.get_input("videoCheckerInput")
        dataManager_gui_output = self.service.get_output("dataManagerVideoEffectsOutput")

        while self.service.running == 1:   #pętla główna
            try:
                with self.service.filters_lock:     #blokada wątku
                    filter_values = {}
                    filter_values['source_port_start'] = int(self.service.get_parameter("source_port_start"))
                    filter_values['source_port_end']     = int(self.service.get_parameter("source_port_end"))
                    filter_values['target_port_start']   = int(self.service.get_parameter("target_port_start"))
                    filter_values['target_port_end']     = int(self.service.get_parameter("target_port_end"))
                    filter_values['source_addres_start'] = str(self.service.get_parameter("source_addres_start"))
                    filter_values['source_addres_end']   = str(self.service.get_parameter("source_addres_end"))
                    filter_values['target_addres_start'] = str(self.service.get_parameter("target_addres_start"))
                    filter_values['target_addres_end']   = str(self.service.get_parameter("target_addres_end"))
                    #filter_values['http']                = self.service.get_parameter("http")
                    #print filter_values
                    self.manager.onGUISetFilter(filter_values)
    
                data = videoChecker_input.read() #obiekt interfejsu
                #print "received from video checker " + str(len(data))
                
                try:
                    #print "v ch bef " + data
                    packetData = decode(data)
                    #print "v ch " + str(packetData)
                    #print "DATAMGR packetData size: " + str(len(data))
                    if not packetData == None:
                        self.manager.receiveVideoChecker(packetData['data'], dataManager_gui_output)
                except Exception, e:
                #    print "some error " + e.message
                    pass
                
            except EOFError:
              #  print "EOFError"
                pass

class GUIThread(threading.Thread):
    def __init__(self, service, manager):
         super(GUIThread, self).__init__()
         self.service = service
         self.manager = manager

    def run(self):
        print "DataManager::guiInputThread started!"
        gui_input = self.service.get_input("guiInput")

        while self.service.running == 1:   #pętla główna
            try:
                data = gui_input.read() #obiekt interfejsu

                try:
                    packetData = decode(data)
                    if not packetData == None:
                        print "big id " + str(packetData['body'])
                        self.manager.setBigImage(packetData['body'])
                except Exception, e:
                    pass
                
            except EOFError:
                pass


class DataManagerService(Service):
    running = 1
    
    def __init__(self):
        Service.__init__(self)

        self.manager = dataManager(self)
        self.filters_lock = threading.RLock()

        signal.signal(signal.SIGINT,  self.stop)
        signal.signal(signal.SIGTSTP, self.stop)

    def stop(self):
        print "stopped"
        self.running = 0
        sys.exit(0)
        print "stop in self"

    def declare_inputs(self):
        self.declare_input("wireInput", InputMessageConnector(self))
        self.declare_input("videoCheckerInput", InputMessageConnector(self))
        self.declare_input("guiInput", InputMessageConnector(self))

    def declare_outputs(self):
        self.declare_output("dataManagerVideoEffectsOutput", OutputMessageConnector(self))
        self.declare_output("dataManagerVideoCheckerOutput", OutputMessageConnector(self))

    def run(self):	#główna metoda
        self.manager.setdataManagerVideoEffectsOutput(self.get_output("dataManagerVideoEffectsOutput"))
        print "DataManager service started!"
        thread1 = WireThread(self, self.manager)
        thread2 = VideoCheckerThread(self, self.manager)
        thread3 = GUIThread(self, self.manager)
        thread1.start() # This actually causes the thread to run
        thread2.start()
        thread3.start()
        thread1.join()  # This waits until the thread has completed
        thread2.join()
        thread3.join()

if __name__=="__main__":
    sc = ServiceController(DataManagerService, "dataManager_service.json")
    sc.start()

