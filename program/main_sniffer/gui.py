from Tkinter import *
import Tkinter as Tk
from PIL import Image, ImageTk

import socket, sys
from struct import *
import threading

from thread import start_new_thread
from cStringIO import StringIO

import signal


#####################################################################
##                                                                 ##
##                              wire                               ##
##                       (+ GUI - obecnie)                         ##
#####################################################################

class myThread (threading.Thread):
    def __init__(self, threadID, name, mainObject):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.mainObject = mainObject
    def run(self):
        print "alfa 0.2 testing"
        self.mainObject.readingThread("running",self.mainObject)


class MyApp(object):
    TextPacket = 0
    mainSocket = 0
    nextPacket = 0

    nextTCP = 0
    nextUDP = 0

    running = 1

    nextPCK = 0

    def __init__(self, parent):
        kolor1='#777777'
        kolor2='#555555'
        kolor3='#aaaaaa'
        self.root = parent
        self.root.title("Sniffer video")
        self.frame = Tk.Frame(parent)
        self.frame.pack()
        
        self.root.protocol('WM_DELETE_WINDOW', self._stop_program)
        signal.signal(signal.SIGINT,  self._stop_program)
        signal.signal(signal.SIGTSTP, self._stop_program)

        #ramka zawierajaca opcje filtracji
        labelfiltracja = LabelFrame(root,bg=kolor3)
        labelfiltracja.place(width = 200, height = 768)

        #poczatek zakresu ip
        label1=Label(labelfiltracja, text='Poczatek zakresu IP:',bg=kolor3)
        label1.place(x=10,y=20)
        entry1=Entry(labelfiltracja)
        entry1.place(x=10,y=50)

        #koniec zakresu ip
        label2=Label(labelfiltracja, text='Koniec zakresu IP:',bg=kolor3)
        label2.place(x=10,y=80)
        entry2=Entry(labelfiltracja)
        entry2.place(x=10,y=110)

        #poczatek zakresu portow
        label3=Label(labelfiltracja, text='Poczatek zakresu portow:',bg=kolor3)
        label3.place(x=10,y=140)
        entry3=Entry(labelfiltracja)
        entry3.place(x=10,y=170)

        #koniec zakresu portow
        label4=Label(labelfiltracja, text='Koniec zakresu portow:',bg=kolor3)
        label4.place(x=10,y=200)
        entry4=Entry(labelfiltracja)
        entry4.place(x=10,y=230)

        #wybor protokolow

        wybor1=IntVar()
        wybor2=IntVar()
        wybor3=IntVar()
        wybor4=IntVar()

        check1=Checkbutton(labelfiltracja, text='HTTP', variable=wybor1, onvalue=1, offvalue=0, bg=kolor3)
        check1.place(x=10, y=260)

        check2=Checkbutton(labelfiltracja, text='protokol2', variable=wybor2, onvalue=1, offvalue=0, bg=kolor3)
        check2.place(x=10, y=290)


        check3=Checkbutton(labelfiltracja, text='protokol3', variable=wybor3, onvalue=1, offvalue=0, bg=kolor3)
        check3.place(x=10, y=320)

        check4=Checkbutton(labelfiltracja, text='protokol4', variable=wybor4, onvalue=1, offvalue=0, bg=kolor3)
        check4.place(x=10, y=350)


        buttonfiltruj=Button(labelfiltracja, text='Filtruj')
        buttonfiltruj.place(x=65, y=700)


        #czesc z miniaturami i ich danymi
        labelminiatury = LabelFrame(root,bg=kolor3)
        labelminiatury.place(x=200,width = 180, height = 768)

        # tu w jakis sposob bedzie trzeba dynamicnzie powielic te elementy to jest tylko dla przykladu

        miniatura=Label(labelminiatury, bg=kolor2)
        miniatura.place(x=10, y=10, width=160, height=120)

        opis1=Label(labelminiatury, text='Adres zrodlowy:',bg=kolor3)
        opis1.place(x=10,y=160)

        opis2=Label(labelminiatury, text='Adres doecelowy:',bg=kolor3)
        opis2.place(x=10,y=190)

        opis2=Label(labelminiatury, text='Port:',bg=kolor3)
        opis2.place(x=10,y=220)


        #okno podgladu (te duze)
        labelpodglad = LabelFrame(root,bg=kolor3)
        labelpodglad.place(x=380,width = 644, height = 768)

        #tutaj nie wiem jak ogrnac tego strema aby byl wrzucam tylko labela zeby bylo wiadomo w ktorym miejscu
        labelpodgladu=Label(labelpodglad, bg=kolor2)
        labelpodgladu.place(x=10, y=10, width=620, height=480)

        label7=Label(labelpodglad, text='Adres zrodlowy:',bg=kolor3)
        label7.place(x=10,y=660)

        label8=Label(labelpodglad, text='Adres doecelowy:',bg=kolor3)
        label8.place(x=10,y=690)

        label9=Label(labelpodglad, text='Port:',bg=kolor3)
        label9.place(x=10,y=720)






        #btn = Tk.Button(self.frame, text="Start Sniffing", command=self.CreateSocketConnection)
        #btn.pack()

        # self.panel = Tk.Label(root)
        # self.panel.pack(side = "bottom", fill = "both", expand = "yes")
        # self.panel2 = Tk.Label(root)
        # self.panel2.pack(side = "bottom", fill = "both", expand = "yes")


    def hide(self):
        self.root.withdraw()

    def _stop_program(self, signal=None, frame=None):
        self.running = 0
        self.root.destroy()

    # def setImage(self, image):
    #     img2 = ImageTk.PhotoImage(image)
    #     self.panel.configure(image = img2)
    #     self.panel.image = img2
    #
    # def setImage2(self, image):
    #     img2 = ImageTk.PhotoImage(image)
    #     self.panel2.configure(image = img2)
    #     self.panel2.image = img2


    def show(self):
        self.root.update()
        self.root.deiconify()



if __name__ == "__main__":
    root = Tk.Tk()
    root.geometry("1024x768")
    root.resizable(width=FALSE, height=FALSE)

    app = MyApp(root)
    root.mainloop()
