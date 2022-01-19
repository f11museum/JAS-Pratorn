from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import QTimer,QDateTime, QFile, QTextStream
from PyQt5.QtMultimedia import QSound


import sys
import json
import random
import argparse
import datetime
import os
import time
import colorsys
import traceback
import threading

from pathlib import Path
import XPlaneUdp


LISTEN_PORT = 49005
SEND_PORT = 49000
XPLANE_IP = "192.168.0.18"


# Egna  funktioner
current_milli_time = lambda: int(round(time.time() * 1000))


parser = argparse.ArgumentParser()
parser.add_argument("--nogui", help="Run without GUI", action="store_true")
parser.add_argument("--file", help="Run selected file, use with --nogui")
args = parser.parse_args()
if args.nogui:
    GUI = False
    print("GUI turned off")
else:
    GUI = True



def signal_handler(sig, frame):
        print("You pressed Ctrl+C!")
        running = False
        sys.exit(0)
        os._exit(0)

class SoundEffect():
    def __init__(self, parent, dataref, name):
        self.parent = parent
        self.dataref = dataref
        self.name = name
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.qs = QSound( os.path.join(current_dir, "../sounds/"+self.name+".wav") )
        

    def buttonPressed(self):
        print("buttonPressed2:", self.dataref)
        self.parent.xp.sendDataref(self.dataref, 1)

class RunGUI(QMainWindow):
    def __init__(self,):
        super(RunGUI,self).__init__()

        self.running = True
        self.soundList = []
        self.currentSound = 0
        self.soundPlaying = -1
        self.soundPlayingType = 0
        self.xp = XPlaneUdp.XPlaneUdp(XPLANE_IP,SEND_PORT)
        self.xp.getDataref("sim/flightmodel/position/indicated_airspeed",1)

        self.xp.getDataref("JAS/autopilot/att",1)
        self.xp.getDataref("JAS/lamps/hojd",1)
        
        
        self.q = QSound("sounds/systemtest.wav")
        self.q.play()
        
        self.initUI()
        
    def initUI(self):
        #self.root = Tk() # for 2d drawing

        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(os.path.join(current_dir, "../ui/main.ui"), self)
        
        #self.setGeometry(200, 200, 300, 300)
        #self.resize(640, 480)
        self.setWindowTitle("Pratorn")
        

        self.ui.test.clicked.connect(self.buttonTest)
        self.ui.button_quit.clicked.connect(self.buttonQuit)
        
        self.initSounds()
        self.timer = QTimer()
        self.timer.timeout.connect(self.loop)
        self.timer.start(100)

    def initSounds(self):
        self.soundList.append(SoundEffect(self, "JAS/pratorn/tal/spak", "tal/spak"))
        self.soundList.append(SoundEffect(self, "JAS/pratorn/tal/taupp", "tal/taupp"))
        self.soundList.append(SoundEffect(self, "JAS/pratorn/tal/okapadrag", "tal/okapadrag"))
        self.soundList.append(SoundEffect(self, "JAS/pratorn/tal/alfa12", "tal/alfa12"))
        self.soundList.append(SoundEffect(self, "JAS/pratorn/tal/fix", "tal/fix"))
        self.soundList.append(SoundEffect(self, "JAS/pratorn/tal/minskafart", "tal/minskafart"))
        self.soundList.append(SoundEffect(self, "JAS/pratorn/tal/ejtils", "tal/ejtils"))
        self.soundList.append(SoundEffect(self, "JAS/pratorn/tal/hojd", "tal/hojd"))
        self.soundList.append(SoundEffect(self, "JAS/pratorn/tal/marktryckfel", "tal/marktryckfel"))
        self.soundList.append(SoundEffect(self, "JAS/pratorn/tal/transsonik", "tal/transsonik"))
        self.soundList.append(SoundEffect(self, "JAS/pratorn/tal/systemtest", "tal/systemtest"))
        
        self.soundList.append(SoundEffect(self, "JAS/pratorn/larm/mkv", "larm/mkv"))
        self.soundList.append(SoundEffect(self, "JAS/pratorn/larm/transsonik", "larm/9beep"))
        self.soundList.append(SoundEffect(self, "JAS/pratorn/larm/gransvarde", "larm/9beep"))
    

        pass

    def updateGUI(self):
        pass
            
    def buttonTest(self):
        print("button test")
        pass
        
    def buttonQuit(self):
        print("button quit")
        self.running = False
        sys.exit(0)
        os._exit(0)
    
    def loop(self):
        # print("loop")
        self.xp.readData()
        if (self.soundPlaying != -1):
            if (self.soundList[self.soundPlaying].qs.isFinished()):
                
                if (self.soundPlayingType == 1):
                    self.xp.sendDataref(self.soundList[self.soundPlaying].dataref, 0)
                    print("stoppar ljud", self.soundPlaying)
                    
                self.soundPlaying = -1
                self.currentSound += 1
                if (self.currentSound>=len(self.soundList)):
                    self.currentSound = 0
            else:
                return
        
        for i in range(len(self.soundList)):
            
            status = self.xp.getDataref(self.soundList[self.currentSound].dataref,10)
            if (status == 1):
                self.soundList[self.currentSound].qs.play()
                self.soundPlaying = self.currentSound
                self.soundPlayingType = 1
                print("startar ljud", self.currentSound)
                self.xp.sendDataref(self.soundList[self.soundPlaying].dataref, 0)
                
                return
            if (status == 2):
                self.soundList[self.currentSound].qs.play()
                self.soundPlaying = self.currentSound
                self.soundPlayingType = 2
                return
            if (status == 3): # Ej klart, ska spela mindre ofta va det tänkt
                self.soundList[self.currentSound].qs.play()
                self.soundPlaying = self.currentSound
                self.soundPlayingType = 3
                return
            
            self.currentSound += 1
            if (self.currentSound>=len(self.soundList)):
                self.currentSound = 0
            # print("soundlist", se.name)
            
        
        #print(self.xp.dataList)
        self.timer.start(10)
        pass
        

if __name__ == "__main__":

    try:
        app = QApplication(sys.argv)
        win = RunGUI()
        win.show()
        sys.exit(app.exec_())
    except Exception as err:
        exception_type = type(err).__name__
        print(exception_type)
        print(traceback.format_exc())
        os._exit(1)
    print ("program end")
    os._exit(0)