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
        self.storage[key] = 'big'

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
        self.root = parent
        self.root.title("Main frame")
        self.frame = Tk.Frame(parent)
        self.frame.pack()
        
        self.root.protocol('WM_DELETE_WINDOW', self._stop_program)
        signal.signal(signal.SIGINT,  self._stop_program)
        signal.signal(signal.SIGTSTP, self._stop_program)
 
        #btn = Tk.Button(self.frame, text="Start Sniffing", command=self.CreateSocketConnection)
        #btn.pack()

        self.panel = Tk.Label(root)
        self.panel.pack(side = "bottom", fill = "both", expand = "yes")
        self.panel2 = Tk.Label(root)
        self.panel2.pack(side = "bottom", fill = "both", expand = "yes")

        self.CreateSocketConnection()
    def hide(self):
        self.root.withdraw()

    def _stop_program(self, signal=None, frame=None):
        self.running = 0
        self.root.destroy()

    def setImage(self, image):
        img2 = ImageTk.PhotoImage(image)
        self.panel.configure(image = img2)
        self.panel.image = img2

    def setImage2(self, image):
        img2 = ImageTk.PhotoImage(image)
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
    root.geometry("800x600")
    app = MyApp(root)
    root.mainloop()

