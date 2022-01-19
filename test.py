import socket
import struct
import binascii
import time


LISTEN_PORT = 49005
SEND_PORT = 49000
XPLANE_IP = "192.168.0.18"


class XPlaneUdp:
    
    def __init__(self, ip, port):
        self.xip = ip
        self.xport = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", LISTEN_PORT))
        self.sendList = []
        self.dataList = {}
        
    def readData(self):
        
        data, addr = self.sock.recvfrom(1024)
        # print("received data:")
        # print(addr)
        # print(data)
        header=data[0:5]
        if(header==b"RREF,"):
            values =data[5:]
            lenvalue = 8
            numvalues = int(len(values)/lenvalue)
            for i in range(0,numvalues):
                singledata = data[(5+lenvalue*i):(5+lenvalue*(i+1))]
                (idx,value) = struct.unpack("if", singledata)
                #print("found values", idx, value)
                self.dataList[self.sendList[idx]] = value
        
    def sendDataref(self, dataref, value):
        message = b'DREF0'
        message = message + struct.pack("f", float(value))
        bytestring = dataref.encode()
        message = message + bytestring + b'\00'
        #print(message)
        
        for i in range(509):
            message = message+b'\x20'

        message = message[:509]

        self.sock.sendto(message, (self.xip, self.xport))
        
    def getDataref(self, dataref, interval):
        self.sendList.append(dataref)
        self.dataList[dataref] = 0
        index = len(self.sendList) - 1
        #print("getDataref ", index)
        message = b'RREF0'
        message = message + struct.pack("i", interval)
        message = message + struct.pack("i", index)
        bytestring = dataref.encode()
        message = message + bytestring + b'\00'
        cmd = b"RREF\x00"
        message = struct.pack("<5sii400s", cmd, interval, index, bytestring)
        assert(len(message)==413)
        #print(message)


        self.sock.sendto(message, (self.xip, self.xport))


xp = XPlaneUdp(XPLANE_IP,SEND_PORT)
xp.getDataref("sim/flightmodel/position/indicated_airspeed",1)

xp.getDataref("JAS/autopilot/att",1)
xp.sendDataref("sim/cockpit/electrical/night_vision_on", 1)
time.sleep(1)
xp.sendDataref("sim/cockpit/electrical/night_vision_on", 0)

# 
while(1):
    xp.readData()
    print(xp.dataList)