#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputStreamConnector, OutputStreamConnector
from ComssServiceDevelopment.service import Service, ServiceController

from struct import *
import threading

import signal


from Tkinter import *
import Tkinter as Tk
from PIL import Image, ImageTk

import socket, sys

from thread import start_new_thread
from cStringIO import StringIO


from Coder.encode import encode
from Coder.decode import decode


##############
## nowe GUI ##
##############

class GUI(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        self.root = Tk.Tk()
        self.root.protocol('WM_DELETE_WINDOW', self._stop_program)
        self.root.geometry("1024x768")
        self.root.resizable(width=FALSE, height=FALSE)

        kolor1='#777777'
        kolor2='#555555'
        kolor3='#aaaaaa'
        self.root.title("Main frame")
        self.frame = Tk.Frame(self.root)
        self.frame.pack()

        #ramka zawierajaca opcje filtracji
        labelfiltracja = LabelFrame(self.root,bg=kolor3)
        labelfiltracja.place(width = 210, height = 768)

        #poczatek zakresu ip
        label1=Label(labelfiltracja, text='Poczatek zrodlowych aresow IP:',bg=kolor3)
        label1.place(x=5,y=20)
        entry1=Entry(labelfiltracja)
        entry1.place(x=5,y=50)

        #koniec zakresu ip
        label2=Label(labelfiltracja, text='Koniec zrodlowych aresow IP:',bg=kolor3)
        label2.place(x=5,y=80)
        entry2=Entry(labelfiltracja)
        entry2.place(x=5,y=110)

        #poczatek zakresu portow
        label3=Label(labelfiltracja, text='Poczatek zrodlowych portow:',bg=kolor3)
        label3.place(x=5,y=140)
        entry3=Entry(labelfiltracja)
        entry3.place(x=5,y=170)

        #koniec zakresu portow
        label4=Label(labelfiltracja, text='Koniec zrodlowych portow:',bg=kolor3)
        label4.place(x=5,y=200)
        entry4=Entry(labelfiltracja)
        entry4.place(x=5,y=230)

        label5=Label(labelfiltracja, text='Poczatek docelowych aresow IP:',bg=kolor3)
        label5.place(x=5,y=260)
        entry5=Entry(labelfiltracja)
        entry5.place(x=5,y=290)

        #koniec zakresu ip
        label6=Label(labelfiltracja, text='Koniec docelowych aresow IP:',bg=kolor3)
        label6.place(x=5,y=320)
        entry6=Entry(labelfiltracja)
        entry6.place(x=5,y=350)

        #poczatek zakresu portow
        label7=Label(labelfiltracja, text='Poczatek docelowych portow:',bg=kolor3)
        label7.place(x=5,y=380)
        entry7=Entry(labelfiltracja)
        entry7.place(x=5,y=410)

        #koniec zakresu portow
        label8=Label(labelfiltracja, text='Koniec docelowych portow:',bg=kolor3)
        label8.place(x=5,y=440)
        entry8=Entry(labelfiltracja)
        entry8.place(x=5,y=470)

        #wybor protokolow

        wybor1=IntVar()
        wybor2=IntVar()
        wybor3=IntVar()
        wybor4=IntVar()

        check1=Checkbutton(labelfiltracja, text='HTTP', variable=wybor1, onvalue=1, offvalue=0, bg=kolor3)
        check1.place(x=5, y=500)

        check2=Checkbutton(labelfiltracja, text='protokol2', variable=wybor2, onvalue=1, offvalue=0, bg=kolor3)
        check2.place(x=5, y=530)


        check3=Checkbutton(labelfiltracja, text='protokol3', variable=wybor3, onvalue=1, offvalue=0, bg=kolor3)
        check3.place(x=5, y=560)

        check4=Checkbutton(labelfiltracja, text='protokol4', variable=wybor4, onvalue=1, offvalue=0, bg=kolor3)
        check4.place(x=5, y=590)


        buttonfiltruj=Button(labelfiltracja, text='Filtruj')
        buttonfiltruj.place(x=65, y=700)


        #czesc z miniaturami i ich danymi
        labelminiatury = LabelFrame(self.root,bg=kolor3)
        labelminiatury.place(x=210,width = 180, height = 768)

        # tu w jakis sposob bedzie trzeba dynamicnzie powielic te elementy to jest tylko dla przykladu

        self.panel2 = Tk.Label(labelminiatury)
        self.panel2.place(x=10, y=10, width=160, height=120)

        opis1=Label(labelminiatury, text='Adres zrodlowy:',bg=kolor3)
        opis1.place(x=10,y=160)

        opis2=Label(labelminiatury, text='Adres doecelowy:',bg=kolor3)
        opis2.place(x=10,y=190)

        opis2=Label(labelminiatury, text='Port:',bg=kolor3)
        opis2.place(x=10,y=220)


        #okno podgladu (te duze)
        labelpodglad = LabelFrame(self.root,bg=kolor3)
        labelpodglad.place(x=390,width = 634, height = 768)

        #tutaj nie wiem jak ogrnac tego strema aby byl wrzucam tylko labela zeby bylo wiadomo w ktorym miejscu
        self.panel = Tk.Label(labelpodglad)
        self.panel.place(x=5, y=10, width=620, height=480)

        label9=Label(labelpodglad, text='Adres zrodlowy:',bg=kolor3)
        label9.place(x=10,y=660)

        label10=Label(labelpodglad, text='Adres doecelowy:',bg=kolor3)
        label10.place(x=10,y=690)

        label11=Label(labelpodglad, text='Port:',bg=kolor3)
        label11.place(x=10,y=720)

        self.root.mainloop()

    def hide(self):
        self.root.withdraw()

    def _stop_program(self, signal=None, frame=None):
        print "stopped"
        self.root.destroy()

    def SIm(self, key, data_body):
        try:
            im = Image.open(StringIO(data_body))
            try:
                im.load()
            except IOError:
                pass
            self.setImage(im)
        except Exception, e:
            "not able to set " + e.message

    def setImage(self, image):
        temp=image.resize((620, 480), Image.ANTIALIAS)
        img2 = ImageTk.PhotoImage(temp)
        self.panel.configure(image = img2)
        self.panel.image = img2


    def setImage2(self, image):

        #img2 = ImageTk.PhotoImage(image)
       # print img2.width()
        temp=image.resize((160, 120), Image.ANTIALIAS)
        img2= ImageTk.PhotoImage(temp)

        # skala_szer=160/img2.width()
        # skala_wysok=120/img2.height()
        # img2.zoom(skala_szer, skala_wysok)
        self.panel2.configure(image = img2)
        self.panel2.image = img2

    def show(self):
        self.root.update()
        self.root.deiconify()


class GuiService(Service):
    running = 1

    def __init__(self):
        Service.__init__(self)
        self.gui = GUI()
        signal.signal(signal.SIGINT,  self.stop)
        signal.signal(signal.SIGTSTP, self.stop)

    def stop(self):
        self.running = 0
        print "stop in self"
        #self.gui._stop_program()

    def declare_inputs(self):
        self.declare_input("dataManagerStreamInput", InputStreamConnector(self))
        
    def declare_outputs(self):	#deklaracja wyjść
        self.declare_output("guiOutput", OutputStreamConnector(self))

    # GŁÓWNA METODA USŁUGI
    def run(self):
        dataManager_input = self.get_input("dataManagerStreamInput")
        print "Gui service started."
        while self.running == 1:
            data = dataManager_input.read()
            packetData = decode(data)
            if not packetData == None:
                if packetData['data']['type'] == 'key':
                    #key is in packetData['data']['body']; more info in packetData['data']['data']
                    pass
                elif packetData['data']['type'] == 'packet':
                    self.gui.SIm(packetData['data']['key'], packetData['body'])

if __name__=="__main__":
    sc = ServiceController(GuiService, "gui_service.json")
    sc.start()

