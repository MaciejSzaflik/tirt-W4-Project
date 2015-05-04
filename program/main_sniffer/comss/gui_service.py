#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputStreamConnector
from ComssServiceDevelopment.service import Service, ServiceController

from struct import *
import threading

import signal

class GuiService(Service):

    running = 1

    def declare_inputs(self):
        self.declare_input("dataManagerInput", InputStreamConnector(self))
        
    def declare_outputs(self):	#deklaracja wyjść
        pass

    # GŁÓWNA METODA USŁUGI
    def run(self):
        dataManager_input = self.get_input("dataManagerInput")
        print "Gui service started."
        while self.running == 1:
            toDisplay = dataManager_input.read()
            print toDisplay

if __name__=="__main__":
    sc = ServiceController(GuiService, "gui_service.json")
    sc.start()
