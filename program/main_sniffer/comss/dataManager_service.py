#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputStreamConnector
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import OutputStreamConnector
from ComssServiceDevelopment.service import Service, ServiceController

class DataManagerService(Service):

    running = 1

    def declare_inputs(self):
        self.declare_input("videoCheckerInput", InputStreamConnector(self))
        
    def declare_outputs(self):
        self.declare_output("dataManagerOutput", OutputStreamConnector(self))
        
    def run(self):	#główna metoda
    
        print "DataManager service started!"
        
        videoChecker_input = self.get_input("videoCheckerInput")
        #dataManager_output = self.get_output("dataManagerOutput")

        while self.running == 1:   #pętla główna
            try:
                imgarray = videoChecker_input.read() #obiekt interfejsu
                print imgarray
                #dataManager_output.send(imgarray)
                
            except EOFError:
                print "EOFError"
                pass
            #except socket.error:
            #    pass

if __name__=="__main__":
    sc = ServiceController(DataManagerService, "dataManager_service.json")
    sc.start()
