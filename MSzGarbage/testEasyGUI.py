from Tkinter import *
import Tkinter as Tk

import socket, sys
from struct import *
import threading

class myThread (threading.Thread):
    def __init__(self, threadID, name, mainObject):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.mainObject = mainObject
    def run(self):
        print "alfa testing"
        self.mainObject.simpleReadingThread("pff",self.mainObject)
 
class MyApp(object):
    TextTcp = 0
    TextUdp = 0
    TextICMP = 0
    TextMAC = 0
    TextIP = 0
    TextPacket = 0
    mainSocket = 0
    nextPacket = 0

    running = 1

    def __init__(self, parent):
        self.root = parent
        self.root.title("Main frame")
        self.frame = Tk.Frame(parent)
        self.frame.pack()
        
        self.root.protocol('WM_DELETE_WINDOW', self.stop_running)
 
        btn = Tk.Button(self.frame, text="Start Sniffing", command=self.CreateSocketConnection)
        btn.pack()
        self.TextPacket = Text(root, height=1, width=40)
        self.TextPacket.pack()
        self.TextMAC = Text(root, height=2, width=200)
        self.TextMAC.pack()
        self.TextIP = Text(root, height=2, width=200)
        self.TextIP.pack()
        self.TextTcp = Text(root, height=4, width=200)
        self.TextTcp.pack()
        self.TextUdp = Text(root, height=4, width=200)
        self.TextUdp.pack()
        self.TextICMP = Text(root, height=4, width=200)
        self.TextICMP.pack()
        
    def hide(self):
        self.root.withdraw()
        
    def stop_running(self):
        self.running = 0
        self.root.destroy()
 
    def CreateSocketConnection(self):
        if self.mainSocket == 0 :
            try:
                self.mainSocket = socket.socket( socket.AF_PACKET , socket.SOCK_RAW , socket.ntohs(0x0003))
            except socket.error , msg:  
                print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
                sys.exit()   
                
            try:
                thread1 = myThread(1,"alfa",self)
                thread1.start()
            except:
                print "Error: unable to start thread" 
               
        else :
            print("pff")
        
 
    def show(self):
        self.root.update()
        self.root.deiconify()
        
    def readPacketFromSocket(self,obj):
        packet = obj.mainSocket.recvfrom(65565)  
        obj.decipherWhatIsInside(packet)
        
        
    def simpleReadingThread(self,threadName, obj):
        while self.running == 1 :
            obj.readPacketFromSocket(obj)
            
            
    def decipherWhatIsInside(self,packet):
        #parse ethernet header
        packet = packet[0]
        eth_length = 14
         
        eth_header = packet[:eth_length]
        eth = unpack('!6s6sH' , eth_header)
        eth_protocol = socket.ntohs(eth[2])
        self.TextMAC.delete(1.0,END)
        self.TextMAC.insert(END,'Destination MAC : ' + self.eth_addr(packet[0:6]) + ' Source MAC : ' + self.eth_addr(packet[6:12]) + ' Protocol : ' + str(eth_protocol))
     
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
            self.TextIP.delete(1.0,END)
            self.TextIP.insert(END, 'Version: ' + str(version) + ' IP Header Length: ' + str(ihl) + ' TTL : ' + str(ttl) + ' Protocol: ' + str(protocol) + ' Source Address: ' + str(s_addr) + ' Destination Address : ' + str(d_addr))

            self.nextPacket = self.nextPacket + 1
            self.TextPacket.delete(1.0,END)
            self.TextPacket.insert(END, 'next: ' + str(self.nextPacket))

            self.TextTcp.delete(1.0,END)
            self.TextUdp.delete(1.0,END)
            self.TextICMP.delete(1.0,END)
            if protocol == 6 :
#               self.TextTcp.delete(1.0,END)
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
                 
                self.TextTcp.insert(END, ' Source Port: ' + str(source_port) + ' Dest Port: ' + str(dest_port) + ' Sequence Number: ' + str(sequence) + ' Acknowledgement: ' + str(acknowledgement) + ' TCP header length : ' + str(tcph_length))
                 
                h_size = eth_length + iph_length + tcph_length * 4
                data_size = len(packet) - h_size
                 
                #get data from the packet
                data = packet[h_size:]
                 
                self.TextTcp.insert(END, ' Data : ' + data)
            elif protocol == 1 & False:
#               self.TextICMP.insert(END,"ICMP")     
                u = iph_length + eth_length
                icmph_length = 4
                icmp_header = packet[u:u+4]
     
                #now unpack them :)
                icmph = unpack('!BBH' , icmp_header)
                 
                icmp_type = icmph[0]
                code = icmph[1]
                checksum = icmph[2]
                 
                self.TextICMP( 'Type : ' + str(icmp_type) + ' Code : ' + str(code) + ' Checksum : ' + str(checksum))
                 
                h_size = eth_length + iph_length + icmph_length
                data_size = len(packet) - h_size
                 
                #get data from the packet
                data = packet[h_size:]
                 
                self.TextICMP( ' Data : ' + data) 
            elif protocol == 17 :
#               self.TextUdp.delete(1.0,END)
                self.TextUdp.insert(END,"UDP")  
                u = iph_length + eth_length
                udph_length = 8
                udp_header = packet[u:u+8]
     
                #now unpack them :)
                udph = unpack('!HHHH', udp_header)
                 
                source_port = udph[0]
                dest_port = udph[1]
                length = udph[2]
                checksum = udph[3]
                 
                self.TextUdp.insert(END,' Source Port : ' + str(source_port) + ' Dest Port : ' + str(dest_port) + ' Length : ' + str(length) + ' Checksum : ' + str(checksum))
                 
                h_size = eth_length + iph_length + udph_length
                data_size = len(packet) - h_size
                 
                #get data from the packet
                data = packet[h_size:]
                 
                self.TextUdp.insert(END, ' Data : ' + data)
 
    def eth_addr(self,a):
        b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]) , ord(a[1]) , ord(a[2]), ord(a[3]), ord(a[4]) , ord(a[5]))
        return b
     
 
if __name__ == "__main__":
    root = Tk.Tk()
    root.geometry("800x600")
    app = MyApp(root)
    root.mainloop()
