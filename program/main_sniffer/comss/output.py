#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tkinter as tk
import threading

from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector #import modułów konektora msg_stream_connector

from ComssServiceDevelopment.development import DevServiceController #import modułu klasy testowego kontrolera usługi
import cv2 #import modułu biblioteki OpenCV
import numpy as np #import modułu biblioteki Numpy

service_controller = DevServiceController("filter1service.json") #utworzenie obiektu kontroletra testowego, jako parametr podany jest plik konfiguracji usługi, do której "zaślepka" jest dołączana
service_controller.declare_connection("videoOutput", InputMessageConnector(service_controller)) #deklaracja interfejsu wejściowego konektora msg_stream_connector, należy zwrócić uwagę, iż identyfikator musi być zgodny z WYJŚCIEM usługi, do której "zaślepka" jest podłączana


connection = service_controller.get_connection("videoOutput") #utworzenie połączenia wejściwoego należy zwrócić uwagę, iż identyfikator musi być zgodny z WYJŚCIEM usługi, do której "zaślepka" jest podłączana
while True: #główna pętla programu
    obj = connection.read() #odczyt danych z interfejsu wejściowego
    frame = np.loads(obj) #załadownaie ramki do obiektu NumPy
    cv2.imshow('Camera',frame) #wyświetlenie ramki na ekran
    cv2.waitKey(1)