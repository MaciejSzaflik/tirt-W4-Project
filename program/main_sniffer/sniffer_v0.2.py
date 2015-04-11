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
def receiveData(data, body, id, object):
    which = 0

    if len(gui_memory) == 0:
        which = 0
    else:
        which = 1

    key = data['source']['address'] + str(data['source']['port']) + data['target']['address'] + str(data['target']['port'])

    if gui_memory.get(key, None) == None:
        gui_memory[key] = which

    displayData(data, data['body_type'], body, id, object, gui_memory[key])

######
# part of GUI
# decyduje czy strumieniować czy tylko pokazać co jest w środku
#####

def displayData(data, data_type, data_body, id, object, which):
    if data_type == 'jpg':
        im = Image.open(StringIO(data_body))
        try:
            im.load()
        except IOError:
            pass

        if which == 0:
            object.setImage(im)
        elif which == 1:
            object.setImage2(im)

#    import json
 #   print json.dumps(data['target'], sort_keys=True,
  #                indent=4, separators=(',', ': '))
    #print('type ', im.format, im.size, im.mode)
    #im.save('temp/img' + str(id) + '.jpg', format=im.format)


#####################################################################
##                                                                 ##
##                          dataManager                            ##
##                                                                 ##
#####################################################################

def manage(data, parsedVideoPacket_data, id, object):
    receiveData(data, parsedVideoPacket_data, id, object)



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
        data['body_type'] = 'jpg'
        manage(data, imgarray, id, object)
    elif checkJPG(imgarray[37:]):
        data['body_type'] = 'jpg'
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
                #FileTCP.write('TCP #' + str(nextNr) + ': Source Port: ' +
                 #                  str(source_port) + '; Dest Port: ' + str(dest_port) +
                  #                 '; Sequence Number: ' + str(sequence) + '; Acknowledgement: ' +
                   #                str(acknowledgement) + '; TCP header length: ' + str(tcph_length) +
                    #               '\n\nData (' + str(len(data)) + '):\n' + data + '\n\n\n')

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
        print "alfa 0.1 testing"
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

