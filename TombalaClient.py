#FileName: TombalaClient.py
#Author : Ozlem Akbas
#Description : SWE544 Course Project for Tombala Multi Player Game

import sys
import socket
import threading
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import Queue

# Connect to the server
ssoc = socket.socket()
host = "192.168.1.22"
port = 12345
ssoc.connect((host,port))

sendQueue = Queue.Queue()
readQueue = Queue.Queue()
screenQueue = Queue.Queue()

#app = ClientDialog(sendQueue, screenQueue)
# start threads

# start threads
#rt = ReadThread("ReadThread", ssoc, sendQueue, readQueue)
#rt.start()
#wt = WriteThread("WriteThread", ssoc, sendQueue)
#wt.start()

#app.run()