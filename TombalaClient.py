#FileName: TombalaClient.py
#Author : Ozlem Akbas
#Description : SWE544 Course Project for Tombala Multi Player Game

import sys
import socket
import threading
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import Queue


# Class Name: ReadThread
# Description : This class for processing the incoming messages to the socket and
#               deriving user friendly information from the incoming messages
class ReadThread (threading.Thread):
    def __init__(self, name, ssoc, sendQueue, readQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.ssoc = ssoc
        self.nickname = ""
        self.sendQueue = sendQueue
        self.readQueue = readQueue

    def incoming_parser(self, data):

        #The case, message has less than three-character length
        if len(data) < 3:
            response = "ERR"
            self.ssoc.send(response)
            return

        #The case, command root is more than three characters
        if len(data) > 3 and not data[3] == " ":
            response = "ERR"
            self.ssoc.send(response)
            return

        rest = data[4:]     #get the rest of the message, no problem even if data < 4

        #The case, communication ends
        if data[0:3] == "BYE":
            if len(rest) == 0:
                response = "ERR"
                self.ssoc.send(response)
                return

        #The case, registration
        elif data[0:3] == "HEL":
            if len(rest) == 0:
                response = "ERR"
                self.csoc.send(response)
                return
            self.nickname = rest

        #The case, user registration is rejected
        elif data[0:3] == "REJ":
            if len(rest) == 0:
                response = "ERR"
                self.csoc.send(response)
                return

        #The case, user is not authenticated
        elif data[0:3] == "ERL":
            if len(rest) > 0:
                response = "ERR"
                self.csoc.send(response)
                return

        #The case, general message is received
        elif data[0:3] == "SAY":
            if len(rest) == 0:
                response = "ERR"
                self.csoc.send(response)
                return
            #Todo: Handle SOK message on server side
            #response = "SOK"
            #self.csoc.send(response)

    def run(self):
        while True:
            data = self.ssoc.recv(1024)
            print(data)
            #self.incoming_parser(data)

# Class Name: WriteThread
class WriteThread (threading.Thread):
    def __init__(self, name, ssoc, sendQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.ssoc = ssoc
        self.sendQueue = sendQueue

    def run(self):
        while True:
            if self.sendQueue.qsize() > 0:
                queue_message = self.sendQueue.get()
                try:
                    temp = str(queue_message)
                    self.ssoc.send(str(queue_message))
                except socket.error:
                    self.ssoc.close()
                    break
            x = raw_input("Command: ")
            self.ssoc.send(x)

class ClientDialog(QDialog):

    def __init__(self, sendQueue, screenQueue):
        self.sendQueue = sendQueue
        self.screenQueue = screenQueue

        # create a Qt application --- every PyQt app needs one
        self.qt_app = QApplication(sys.argv)

        # Call the parent constructor on the current object
        QDialog.__init__(self, None)

        # Set up the window
        self.setWindowTitle('Tombala Game')
        self.setMinimumSize(500, 200)
        self.resize(640, 480)

        # Add a vertical layout
        self.vbox = QVBoxLayout()
        self.vbox.setGeometry(QRect(10, 10, 621, 461))

        # Add a horizontal layout
        self.hbox = QHBoxLayout()

        # The sender textbox
        self.sender = QLineEdit("", self)

        # The channel region
        self.channel = QTextBrowser()
        self.channel.setMinimumSize(QSize(480, 0))

        # The send button
        self.send_button = QPushButton('&Send')

        # Connect the Go button to its callback
        #self.send_button.clicked.connect(self.outgoing_parser)

        # Add the controls to the vertical layout
        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.sender)
        self.vbox.addWidget(self.send_button)
        self.hbox.addWidget(self.channel)

        # Use the vertical layout for the current window
        self.setLayout(self.vbox)

    #Run the app and show the main form
    def run(self):
        self.show()
        self.qt_app.exec_()

# Connect to the server
ssoc = socket.socket()
host = "192.168.1.22"
port = 12345
ssoc.connect((host,port))

sendQueue = Queue.Queue()
readQueue = Queue.Queue()
screenQueue = Queue.Queue()

app = ClientDialog(sendQueue, screenQueue)
# start threads

# start threads
rt = ReadThread("ReadThread", ssoc, sendQueue, readQueue)
rt.start()
wt = WriteThread("WriteThread", ssoc, sendQueue)
wt.start()

app.run()