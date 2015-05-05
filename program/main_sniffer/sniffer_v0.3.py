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
##                              GUI                                ##
##                                                                 ##
#####################################################################

gui_memory = {}
def GUIAddStream(key, data):
    if gui_memory.get(key, None) == None:
        gui_memory[key] = len(gui_memory)

def GUInextPacket(key, data_type, data_body, id, object):
    if data_type == 'http':
        im = Image.open(StringIO(data_body))
        try:
            im.load()
        except IOError:
            pass
        which = gui_memory[key]
        if which == 0:
            object.setImage(im)
        elif which == 1:
            object.setImage2(im)


#####################################################################
##                                                                 ##
##                          dataManager                            ##
##                                                                 ##
#####################################################################

def manage(data, parsedVideoPacket_data, id, object):
    manager.receiveData(data, parsedVideoPacket_data, id, object)
    

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

    def saveNewPacket(self, packetData):
        key = self.createKey(packetData)
        self.storage[key] = 'small'
        self.GUIAddStream(key, packetData)

    def createKey(self, packetData):
        return packetData['source']['address'] + str(packetData['source']['port']) + packetData['target']['address'] + str(packetData['target']['port'])

    def checkLocally(self, packetData):
        return not self.storage.get(self.createKey(packetData), None) == None

    def resizeBody(self, body, size):
        # somehow resize body witch self.resizeOptions[size]
        return body

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

    def GUIAddStream(self, key, packetData):
        print "GUIAddStream " + key
        GUIAddStream(key, packetData)

    def GUIRemoveStream(self, key):
        print "GUIRemoveStream " + key
        #GUIRemoveStream(key)

    def notifyGUI(self, packetData, parsedVideoPacket_data, id, object):# last 3 args are to be removed
        key = self.createKey(packetData)
        #print "notify " + key
        #GUInextPacket(key, packetData['body_type'], self.resizeBody(body, self.storage.get(key)))
        GUInextPacket(key, packetData['body_type'], self.resizeBody(parsedVideoPacket_data, self.storage.get(key)), id, object)

    # action to be added in main LOOP of comss
    def receiveData(self, packetData, parsedVideoPacket_data, id, object):
        if self.checkLocally(packetData):
            self.notifyGUI(packetData, parsedVideoPacket_data, id, object)
        else:
            if self.checkInFilter(packetData):
                self.saveNewPacket(packetData)
                self.notifyGUI(packetData, parsedVideoPacket_data, id, object)

manager = dataManager()

#####################################################################
##                                                                 ##
##                          videoChecker                           ##
##                                                                 ##
#####################################################################

def checkJPG(imgarray):
    try:
        im = Image.open(StringIO(imgarray))
    except IOError:
        return False

    try:
        im.load()
    except IOError:
        pass

    return True

def anotherCheck(imgarray):
    return False


def checkVideo(data, imgarray, id, object):
    if checkJPG(imgarray):
        data['body_type'] = 'http'
        manage(data, imgarray, id, object)
    elif checkJPG(imgarray[37:]):
        data['body_type'] = 'http'
        manage(data, imgarray[37:], id, object)
    elif anotherCheck(imgarray):
        data['body_type'] = 'never accessed here'
        manage(data, imgarray, id, object)



#####################################################################
##                                                                 ##
##                            unpacker                             ##
##                                                                 ##
#####################################################################

def eth_addr(self,a):
    b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]) , ord(a[1]) , ord(a[2]), ord(a[3]), ord(a[4]) , ord(a[5]))
    return b

def decipherWhatIsInside(packet, nextNr, object):
    #parse ethernet header
    packet = packet[0]
    eth_length = 14

    eth_header = packet[:eth_length]
    eth = unpack('!6s6sH' , eth_header)
    eth_protocol = socket.ntohs(eth[2])

    #Parse IP packets, IP Protocol number = 8
    if eth_protocol == 8 :
        #Parse IP header
        #take first 20 characters for the ip header
        ip_header = packet[eth_length:20+eth_length]

        #now unpack them :)
        iph = unpack('!BBHHHBBH4s4s' , ip_header)

        version_ihl = iph[0]
        version = version_ihl >> 4
        ihl = version_ihl & 0xF

        iph_length = ihl * 4

        ttl = iph[5]
        protocol = iph[6]
        s_addr = socket.inet_ntoa(iph[8]);
        d_addr = socket.inet_ntoa(iph[9]);
        if protocol == 6 :
            t = iph_length + eth_length
            tcp_header = packet[t:t+20]

            #now unpack them :)
            tcph = unpack('!HHLLBBHHH' , tcp_header)

            source_port = tcph[0]
            dest_port = tcph[1]
            sequence = tcph[2]
            acknowledgement = tcph[3]
            doff_reserved = tcph[4]
            tcph_length = doff_reserved >> 4

            h_size = eth_length + iph_length + tcph_length * 4

            #get data from the packet
            body = packet[h_size:]

            data = {}
            data['eth_protocol'] = eth_protocol
            data['version'] = version
            data['ihl'] = ihl
            data['source'] = {}
            data['source']['address'] = s_addr
            data['source']['port'] = source_port
            data['target'] = {}
            data['target']['address'] = d_addr
            data['target']['port'] = dest_port
            data['sequence'] = sequence
            data['acknowledgement'] = acknowledgement
            data['doff_reserved'] = doff_reserved
            data['tcph_length'] = tcph_length
            data['h_size'] = h_size

            if (len(data)) > 0 :#and nextNr < 20 :
                checkVideo(data, body, nextNr, object)

def unpacker(packet, next_nr, object):
    decipherWhatIsInside(packet, next_nr, object)


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
        self.root.title("Main frame")
        self.frame = Tk.Frame(parent)
        self.frame.pack()
        
        self.root.protocol('WM_DELETE_WINDOW', self._stop_program)
        signal.signal(signal.SIGINT,  self._stop_program)
        signal.signal(signal.SIGTSTP, self._stop_program)

        #ramka zawierajaca opcje filtracji
        labelfiltracja = LabelFrame(root,bg=kolor3)
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
        labelminiatury = LabelFrame(root,bg=kolor3)
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
        labelpodglad = LabelFrame(root,bg=kolor3)
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


        self.CreateSocketConnection()
    def hide(self):
        self.root.withdraw()

    def _stop_program(self, signal=None, frame=None):
        self.running = 0
        self.root.destroy()

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



    def CreateSocketConnection(self):
        if self.mainSocket == 0:
            try:
                self.mainSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
            except socket.error, msg:
                print 'Socket could not be created. Error Code: ' + str(msg[0]) + ' Message ' + msg[1]
                sys.exit()
            try:
                thread1 = myThread(1, "alfa", self)
                thread1.start()
            except:
                print "Error: unable to start thread"
        else:
            print("pff")

    def show(self):
        self.root.update()
        self.root.deiconify()

    def readPacketFromSocket(self,obj):
        packet = obj.mainSocket.recvfrom(16384)#65535)
        self.nextPCK = self.nextPCK + 1

        #start_new_thread(unpacker,(packet, self.nextPCK, self))
        unpacker(packet, self.nextPCK, self)

    def readingThread(self, threadName, obj):
        while self.running == 1:
            obj.readPacketFromSocket(obj)


if __name__ == "__main__":
    root = Tk.Tk()
    root.geometry("1024x768")
    root.resizable(width=FALSE, height=FALSE)
    app = MyApp(root)
    root.mainloop()

