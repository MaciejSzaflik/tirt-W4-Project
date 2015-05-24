#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector, OutputMessageConnector
from ComssServiceDevelopment.service import Service, ServiceController
from ComssServiceDevelopment.development import DevServiceController #import modułu klasy testowego kontrolera usługi

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

def resize(width, height, data):
    img = Image.open(StringIO(data))

    try:
        img.load()
    except IOError:
        pass

    img = img.resize((width, height), Image.ANTIALIAS)

    output = StringIO()
    img.save(output, format='JPEG')

    imageData = output.getvalue()
    output.close()

    return imageData

def resizzer(data, size):
    width = 10
    height = 10
    if size == 'big':
        width = 620
        height = 480
    else:
        width = 160
        height = 120
    return resize(width, height, data)

##############
## nowe GUI ##
##############

class GUI(threading.Thread):
    streams = []
    miniatury = []
    ileMiniatur = 0
    bigId = 0
    miniaturaID = 0

    labelminiatury = 0
    labelZ = 0
    labelZVal = 0
    labelDo = 0
    labelDoVal = 0
    kolor1='#777777'
    kolor2='#555555'
    kolor3='#aaaaaa'

    dataManagerController = DevServiceController("dataManager_service.json")

    # protocols checkboxex control variables
    wybor1 = 1
    wybor2 = 0
    wybor3 = 0
    wybor4 = 0
    
    # effects checkboxex control variables
    invertedColors = 0
    monochrome = 0
    blur = 0

    source_addres_start = "127.0.0.1"
    source_addres_end = "127.0.0.1"
    source_port_start = 6000
    source_port_end = 7999
    target_addres_start = "127.0.0.1"
    target_addres_end = "127.0.0.1"
    target_port_start = 1000
    target_port_end = 80000


    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        self.root = Tk.Tk()
        
        #icon = PhotoImage(file=)
        #self.root.iconphoto('@icon.xbm')
        img = PhotoImage(file='icon.png')
        self.root.call('wm', 'iconphoto', self.root._w, img)
        self.root.protocol('WM_DELETE_WINDOW', self._stop_program)
        self.root.geometry("1044x768")
        self.root.resizable(width=FALSE, height=FALSE)

        self.root.title("Main frame")
        
        #self.frame = Tk.Frame(self.root)
       # self.frame.pack()

        #ramka zawierajaca opcje filtracji
        labelfiltracja = LabelFrame(self.root,bg=self.kolor3)
        labelfiltracja.place(width = 210, height = 768)

        #poczatek zakresu ip
        label1=Label(labelfiltracja, text='Poczatek zrodlowych aresow IP:',bg=self.kolor3, wraplength=160)
        label1.place(x=5,y=20)
        self.source_addres_start = StringVar()
        self.source_addres_start.set('127.0.0.1')
        entry1=Entry(labelfiltracja, textvariable=self.source_addres_start)
        entry1.place(x=5,y=50)
        entry1.get()

        #koniec zakresu ip
        label2=Label(labelfiltracja, text='Koniec zrodlowych aresow IP:',bg=self.kolor3)
        label2.place(x=5,y=80)
        self.source_addres_end = StringVar()
        self.source_addres_end.set('127.0.0.1')
        entry2=Entry(labelfiltracja, textvariable=self.source_addres_end)
        entry2.place(x=5,y=110)
        entry2.get()

        #poczatek zakresu portow
        label3=Label(labelfiltracja, text='Poczatek zrodlowych portow:',bg=self.kolor3)
        label3.place(x=5,y=140)
        self.source_port_start = StringVar()
        self.source_port_start.set('6000')
        entry3=Entry(labelfiltracja, textvariable=self.source_port_start)
        entry3.place(x=5,y=170)
        entry3.get()

        #koniec zakresu portow
        label4=Label(labelfiltracja, text='Koniec zrodlowych portow:',bg=self.kolor3)
        label4.place(x=5,y=200)
        self.source_port_end = StringVar()
        self.source_port_end.set('7999')
        entry4=Entry(labelfiltracja, textvariable=self.source_port_end)
        entry4.place(x=5,y=230)
        entry4.get()

        label5=Label(labelfiltracja, text='Poczatek docelowych aresow IP:',bg=self.kolor3)
        label5.place(x=5,y=260)
        self.target_addres_start = StringVar()
        self.target_addres_start.set('127.0.0.1')
        entry5=Entry(labelfiltracja, textvariable=self.target_addres_start)
        entry5.place(x=5,y=290)
        entry5.get()

        #koniec zakresu ip
        label6=Label(labelfiltracja, text='Koniec docelowych aresow IP:',bg=self.kolor3)
        label6.place(x=5,y=320)
        self.target_addres_end = StringVar()
        self.target_addres_end.set('127.0.0.1')
        entry6=Entry(labelfiltracja, textvariable=self.target_addres_end)
        entry6.place(x=5,y=350)
        entry6.get()

        #poczatek zakresu portow
        label7=Label(labelfiltracja, text='Poczatek docelowych portow:',bg=self.kolor3)
        label7.place(x=5,y=380)
        self.target_port_start = StringVar()
        self.target_port_start.set('1000')
        entry7=Entry(labelfiltracja, text=self.target_port_start)
        entry7.place(x=5,y=410)
        entry7.get()

        #koniec zakresu portow
        label8=Label(labelfiltracja, text='Koniec docelowych portow:',bg=self.kolor3)
        label8.place(x=5,y=440)
        self.target_port_end = StringVar()
        self.target_port_end.set('80000')
        entry8=Entry(labelfiltracja, textvariable=self.target_port_end)
        entry8.place(x=5,y=470)
        entry8.get()

        #wybor protokolow

        self.wybor1=IntVar()
        self.wybor1.set(1)
        self.wybor2=IntVar()
        self.wybor2.set(0)
        self.wybor3=IntVar()
        self.wybor3.set(0)
        self.wybor4=IntVar()
        self.wybor4.set(0)

        check1=Checkbutton(labelfiltracja, text='HTTP', variable=self.wybor1, onvalue=1, offvalue=0, bg=self.kolor3)
        check1.place(x=5, y=500)

        check2=Checkbutton(labelfiltracja, text='protokol2', variable=self.wybor2, onvalue=1, offvalue=0, bg=self.kolor3)
        check2.place(x=5, y=530)


        check3=Checkbutton(labelfiltracja, text='protokol3', variable=self.wybor3, onvalue=1, offvalue=0, bg=self.kolor3)
        check3.place(x=5, y=560)

        check4=Checkbutton(labelfiltracja, text='protokol4', variable=self.wybor4, onvalue=1, offvalue=0, bg=self.kolor3)
        check4.place(x=5, y=590)

	buttonusun=Button(labelfiltracja, text='Usun', command=self.removeStream)
        buttonusun.place(x=65, y=670)

        buttonfiltruj=Button(labelfiltracja, text='Filtruj', command=self.updateFilters)
        buttonfiltruj.place(x=65, y=700)

        #czesc z miniaturami i ich danymi
        self.labelminiatury = Canvas(self.root,bg=self.kolor3)

        vbar=Scrollbar(self.root, orient=VERTICAL)

        vbar.config(command=self.labelminiatury.yview)
        vbar.place(x=390, width=20, height=768)

        self.labelminiatury.config(yscrollcommand=vbar.set)
        self.labelminiatury.place(x=210, y=1, width = 180, height = 768)

        self.labelminiatury.configure(scrollregion=(0,0,180,3000))
        #self.labelminiatury.create_line(10, 10, 160, 10)

        # tu w jakis sposob bedzie trzeba dynamicnzie powielic te elementy to jest tylko dla przykladu

        #self.panel2 = Tk.Label(labelminiatury)
        #self.panel2.place(x=10, y=10, width=160, height=120)

        #opis1=Label(labelminiatury, text='Adres zrodlowy:',bg=self.kolor3)
        #opis1.place(x=10,y=160)

        #opis2=Label(labelminiatury, text='Adres doecelowy:',bg=self.kolor3)
        #opis2.place(x=10,y=190)

        #opis2=Label(labelminiatury, text='Port:',bg=self.kolor3)
        #opis2.place(x=10,y=220)

        #okno podgladu (te duze)
        labelpodglad = LabelFrame(self.root,bg=self.kolor3)
        labelpodglad.place(x=410,width = 634, height = 768)
        
        # obrazek tła
        bgImage = PhotoImage(file='background.png')
        labelBgImage = Label(labelpodglad, image=bgImage)
        labelBgImage.place(x=366, y=500)

        #tutaj nie wiem jak ogrnac tego strema aby byl wrzucam tylko labela zeby bylo wiadomo w ktorym miejscu
        self.panel = Tk.Label(labelpodglad)
        self.panel.place(x=5, y=10, width=620, height=480)

        self.labelStreamInfo=Label(labelpodglad, text="Informacje o strumieniu", font="Verdana 14 bold", bg=self.kolor3)
        self.labelStreamInfo.place(x=10,y=500)

        self.labelZVal = StringVar()
        self.labelZVal.set("Z: ")
        self.labelZ=Label(labelpodglad, textvariable=self.labelZVal, font="Verdana 14", bg=self.kolor3)
        self.labelZ.place(x=10,y=530)

        self.labelDoVal = StringVar()
        self.labelDoVal.set("Do: ")
        self.labelDo=Label(labelpodglad, textvariable=self.labelDoVal, font="Verdana 14", bg=self.kolor3)
        self.labelDo.place(x=10,y=555)
        
        self.labelStreamEffects=Label(labelpodglad, text="Efekty", font="Verdana 14 bold", bg=self.kolor3)
        self.labelStreamEffects.place(x=10,y=600)
        
        self.invertedColors=IntVar()
        self.invertedColors.set(0)
        self.monochrome=IntVar()
        self.monochrome.set(0)
        self.blur=IntVar()
        self.blur.set(0)

        checkInvertedColors = Checkbutton(labelpodglad, text='Odwrócone kolory', font="Verdana 14", variable=self.invertedColors, onvalue=1, offvalue=0, bg=self.kolor3)
        checkInvertedColors.place(x=10, y=640)
        
        checkMonochrome = Checkbutton(labelpodglad, text='Odcienie szarości', font="Verdana 14", variable=self.monochrome, onvalue=1, offvalue=0, bg=self.kolor3)
        checkMonochrome.place(x=10, y=680)
        
        checkBlur = Checkbutton(labelpodglad, text='Rozmycie', font="Verdana 14", variable=self.blur, onvalue=1, offvalue=0, bg=self.kolor3)
        checkBlur.place(x=10, y=720)
        
        self.root.mainloop()

    def updateFilters(self):
        self.dataManagerController.update_params({"source_port_start": self.source_port_start.get()})
        self.dataManagerController.update_params({"source_port_end": self.source_port_end.get()})
        self.dataManagerController.update_params({"target_port_start": self.target_port_start.get()})
        self.dataManagerController.update_params({"target_port_end": self.target_port_end.get()})
        self.dataManagerController.update_params({"source_addres_start": self.source_addres_start.get()})
        self.dataManagerController.update_params({"source_addres_end": self.source_addres_end.get()})
        self.dataManagerController.update_params({"target_addres_start": self.target_addres_start.get()})
        self.dataManagerController.update_params({"target_addres_end": self.target_addres_end.get()})
        self.dataManagerController.update_params({"http": True if self.wybor1.get() == 1 else False})

    def addThumbnail(self, streamData):
        miniatura = {}

        miniatura['id'] = streamData['id']

        miniatura['thumbnail'] = Label(self.labelminiatury)
        self.labelminiatury.create_window(10, self.ileMiniatur*180+10, width=160, height=120, window=miniatura['thumbnail'], anchor=NW)
        miniatura['thumbnail'].bind("<Button-1>", self.clickThumbnail)

        miniatura['source'] = Label(self.labelminiatury, text='Z:   ' + str(streamData['source']), bg=self.kolor3)
        self.labelminiatury.create_window(10, self.ileMiniatur*180+130, window=miniatura['source'], anchor=NW)

        miniatura['destination'] = Label(self.labelminiatury, text='Do: ' + str(streamData['target']), bg=self.kolor3)
        self.labelminiatury.create_window(10, self.ileMiniatur*180+150, window=miniatura['destination'], anchor=NW)

        miniatura['yposition'] = self.ileMiniatur*180

        #miniatura.pack()

        self.miniatury.append(miniatura)
        self.ileMiniatur = self.ileMiniatur+1

    def clickThumbnail(self,event):
        widget = event.widget
        miniatura = (item for item in self.miniatury if item['thumbnail'] == widget).next()
        self.bigId = miniatura['id']
        self.miniaturaID = miniatura['id']
        print "bigId:" + str(self.bigId)
        self.bigOutput.send(encode({'type': 'resize'}, self.bigId))
        


    def hide(self):
        self.root.withdraw()

    def _stop_program(self, signal=None, frame=None):
        print "stopped"
        self.root.destroy()

    def SIm(self, id, data_body, body_type, size):
        if body_type == 'http':
            try:
                im = None
                try:
                    im = Image.open(StringIO(resizzer(data_body, size)))
                except Exception, e:
                    print "err"
                    print e.message

                try:
                    im.load()
                except IOError:
                    pass

                if id == self.bigId and size == 'big':
                    self.updateBigImage(id, im)
                elif size == 'small':
      	            self.updateThumbnail(id, im)

                #self.updateThumbnail(id, im)

            except Exception, e:
                print "not able to set " + e.message

    def updateBigImage(self, id, image):
        miniatura = (item for item in self.miniatury if item["id"] == id).next()
        self.labelZVal.set(miniatura['source'].cget("text"))
        #self.labelZ.set(zVal)
        self.labelDoVal.set(miniatura['destination'].cget("text"))
        #temp=image.resize((620, 480), Image.ANTIALIAS)
        img2 = ImageTk.PhotoImage(image)
        self.panel.configure(image = img2)
        self.panel.image = img2


    def updateThumbnail(self, id, image):
        # resize image
        #temp=image.resize((160, 120), Image.ANTIALIAS)
        img2= ImageTk.PhotoImage(image)

        # skala_szer=160/img2.width()
        # skala_wysok=120/img2.height()
        # img2.zoom(skala_szer, skala_wysok)
        miniatura = (item for item in self.miniatury if item["id"] == id).next()
        miniatura['thumbnail'].configure(image = img2)
        miniatura['thumbnail'].image = img2

    def show(self):
        self.root.update()
        self.root.deiconify()

    def removeStream(self):
	print self.miniaturaID
	if not self.miniaturaID==0:
		miniatura = (item for item in self.miniatury if item["id"] == self.miniaturaID).next()
		print 'usuwanie'	
		#self.labelminiatury.destroy(miniatura['thumbnail'])
		miniatura['thumbnail'].destroy()
        	miniatura['source'].destroy() 
       		miniatura['destination'].destroy()
		porownanie=miniatura['yposition']
		#porownanie=porownanie/180
		
		print porownanie
       		self.ileMiniatur = self.ileMiniatur-1
		for i in self.miniatury:
			print i['id']
			print i['id'].index(i['id'])
			if i['yposition'] > porownanie:
				print i['yposition']
				nowyY=(0*180)-170
				miniatura['thumbnail'].configure(y=nowyY)
       				miniatura['thumbnail'].y = nowyY
			
			
	#def addThumbnail(self, streamData):
       # miniatura = {}
##
      #  miniatura['id'] = streamData['id']
#
 #       miniatura['thumbnail'] = Label(self.labelminiatury)
  #      self.labelminiatury.create_window(10, self.ileMiniatur*180+10, width=160, height=120, window=miniatura['thumbnail'], anchor=NW)
   #     miniatura['thumbnail'].bind("<Button-1>", self.clickThumbnail)
#
 #       miniatura['source'] = Label(self.labelminiatury, text='Z:   ' + str(streamData['source']), bg=self.kolor3)
  #      self.labelminiatury.create_window(10, self.ileMiniatur*180+130, window=miniatura['source'], anchor=NW)
#
 #       miniatura['destination'] = Label(self.labelminiatury, text='Do: ' + str(streamData['target']), bg=self.kolor3)
  #      self.labelminiatury.create_window(10, self.ileMiniatur*180+150, window=miniatura['destination'], anchor=NW)
#
 ##       miniatura['yposition'] = self.ileMiniatur*180

        #miniatura.pack()

   #     self.miniatury.append(miniatura)
    #    self.ileMiniatur = self.ileMiniatur+1

    def addStream(self, packetData):
        streamData = {}
        streamData['id'] = packetData['body']
        streamData['source'] = str(packetData['data']['data']['source']['address']) + ":" + str(packetData['data']['data']['source']['port'])
        streamData['target'] = str(packetData['data']['data']['target']['address']) + ":" + str(packetData['data']['data']['target']['port'])
        self.streams.append(streamData)

        self.addThumbnail(streamData)

        self.bigId = streamData['id']
        self.bigOutput.send(encode({'type': 'resize'}, self.bigId))
        print "added stream:" + str(streamData)

    def setBigOutput(self, output):
        self.bigOutput = output


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
        self.declare_input("videoEffectsStreamInput", InputMessageConnector(self))

    def declare_outputs(self):	#deklaracja wyjść
        self.declare_output("guiOutput", OutputMessageConnector(self))

    # GŁÓWNA METODA USŁUGI
    def run(self):
        dataManager_input = self.get_input("videoEffectsStreamInput")
        self.gui.setBigOutput(self.get_output("guiOutput"))

        print "Gui service started."
        while self.running == 1:
            data = dataManager_input.read()
            #print "received from data manager " + str(len(data))
            packetData = decode(data)

            if not packetData == None:

                if packetData['data']['type'] == 'id':
                    #id is in packetData['body']; more info in packetData['data']['data']
                    self.gui.addStream(packetData)
                    pass

                elif packetData['data']['type'] == 'remove':
                    # id jest w body
                    #self.gui.removeStream(packetData)
                    print "REMOVED " + str(packetData['body'])

                elif packetData['data']['type'] == 'packet':
                    #print "notified:" + str(packetData['data'])
                    self.gui.SIm(packetData['data']['id'], packetData['body'], packetData['data']['body_type'], packetData['data']['size'])

if __name__=="__main__":
    sc = ServiceController(GuiService, "gui_service.json")
    sc.start()

