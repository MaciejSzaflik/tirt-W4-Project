#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ComssServiceDevelopment.connectors.udp.multicast import InputMulticastConnector
from ComssServiceDevelopment.service import Service, ServiceController

class UnpackerService(Service): 

    def declare_inputs(self):
        self.declare_input("wireInput", InputMulticastConnector(self))
        
    def declare_outputs(self):
        pass  

    def run(self):	#główna metoda usługi
        wire_input = self.get_input("wireInput") #obiekt interfejsu wyjściowego

        while self.running():   #pętla główna usługi
            data = wire_input.read();
            print data

if __name__=="__main__":
    sc = ServiceController(UnpackerService, "unpacker_service.json")
    sc.start()
