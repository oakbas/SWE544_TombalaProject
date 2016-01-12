#FileName: TombalaClient.py
#Author : Ozlem Akbas
#Description : SWE544 Course Project for Tombala Multi Player Game

import sys
import socket
import threading
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import Queue
import datetime


# Class Name: ReadThread
# Description : This class for processing the incoming messages to the socket and
#               deriving user friendly information from the incoming messages
class ReadThread (threading.Thread):
    def __init__(self, name, ssoc, condition, sendQueue, screenQueue, sessionQueue, sitQueue, cardQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.ssoc = ssoc
        self.nickname = ""
        self.sendQueue = sendQueue
        self.screenQueue = screenQueue
        self.sessionQueue = sessionQueue
        self.sitQueue = sitQueue
        self.condition = condition
        self.cardQueue = cardQueue

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
            screenMsg = "GoodBye " + self.nickname
            self.screenQueue.put(screenMsg)

        #The case, registration
        elif data[0:3] == "HEL":
            if len(rest) == 0:
                response = "ERR"
                self.ssoc.send(response)
                return
            self.nickname = rest

            screenMsg = "Welcome " + self.nickname
            self.screenQueue.put(screenMsg)

        #The case, user registration is rejected
        elif data[0:3] == "REJ":
            if len(rest) == 0:
                response = "ERR"
                self.ssoc.send(response)
                return
            screenMsg = "Please use other nickname"
            self.screenQueue.put(screenMsg)

        #The case, user is not authenticated
        elif data[0:3] == "ERL":
            if len(rest) > 0:
                response = "ERR"
                self.ssoc.send(response)
                return

            screenMsg = "Please log in first"
            self.screenQueue.put(screenMsg)

        #The case, general message is received
        elif data[0:3] == "SAY":
            if len(rest) == 0:
                response = "ERR"
                self.ssoc.send(response)
                return

            #Todo: Handle SOK message on server side
            #response = "SOK"
            #self.ssoc.send(response)
            screenMsg = "General Message: " + rest
            self.screenQueue.put(screenMsg)

        elif data[0:3] == "LSA":
            if len(rest) == 0:
                response = "ERR"
                self.ssoc.send(response)
                return

            splitted = rest.split(";")
            self.sessionQueue.put(splitted)

        elif data[0:3] == "JNA":
            if len(rest) > 0:
                response = "ERR"
                self.ssoc.send(response)
                return

            screenMsg = "Join accepted"
            self.screenQueue.put(screenMsg)

        elif data[0:3] == "JNR":
            if len(rest) == 0:
                response = "ERR"
                self.ssoc.send(response)
                return

            screenMsg = "Join rejected, try again"
            self.screenQueue.put(screenMsg)

        elif data[0:3] == "CSA":
            if len(rest) == 0:
                response = "ERR"
                self.ssoc.send(response)
                return

            screenMsg = "Session created"
            self.screenQueue.put(screenMsg)

        elif data[0:3] == "CSR":
            if len(rest) > 0:
                response = "ERR"
                self.ssoc.send(response)
                return

            screenMsg = "Session could not be created, try again"
            self.screenQueue.put(screenMsg)

        elif data[0:3] == "QGA":
            if len(rest) > 0:
                response = "ERR"
                self.ssoc.send(response)
                return

            screenMsg = "You exit game"
            self.screenQueue.put(screenMsg)

        elif data[0:3] == "STR":
            if len(rest) == 0:
                response = "ERR"
                self.ssoc.send(response)
                return

            screenMsg = "New game is starting with session " + rest
            self.screenQueue.put(screenMsg)

            response = "STA"
            print(response)
            self.ssoc.send(response)

        elif data[0:3] == "INF":
            if len(rest) == 0:
                response = "ERR"
                self.ssoc.send(response)
                return

            splitted = rest.split(":")
            self.sitQueue.put(splitted)

            screenMsg = "Situation of the users " + rest
            self.screenQueue.put(screenMsg)


        elif data[0:3] == "CNA":
            if len(rest) > 0:
                response = "ERR"
                self.ssoc.send(response)
                return

            screenMsg = "Cinko is accepted"
            self.screenQueue.put(screenMsg)

        elif data[0:3] == "CNR":
            if len(rest) > 0:
                response = "ERR"
                self.ssoc.send(response)
                return

            screenMsg = "Cinko is rejected, please control your card"
            self.screenQueue.put(screenMsg)

        elif data[0:3] == "TBA":
            if len(rest) > 0:
                response = "ERR"
                self.ssoc.send(response)
                return

            screenMsg = "Tombala is accepted"
            self.screenQueue.put(screenMsg)

        elif data[0:3] == "TBR":
            if len(rest) > 0:
                response = "ERR"
                self.ssoc.send(response)
                return

            screenMsg = "Tombala is rejected, please control your card"
            self.screenQueue.put(screenMsg)

        elif data[0:3] == "NMB":
            if len(rest) == 0:
                response = "ERR"
                self.ssoc.send(response)
                return

            screenMsg = "New lucky number is " + rest
            self.screenQueue.put(screenMsg)

        elif data[0:3] == "APC":
            if len(rest) == 0:
                response = "ERR"
                self.ssoc.send(response)
                return

            splitted = rest.split(";")
            for s in splitted:
                user = s.split(":")
                if user[0] == self.nickname:
                    myCard = user[1]
                    print myCard
            rows = myCard.split(",")
            self.cardQueue.put(rows)

    def run(self):
        while True:
            data = self.ssoc.recv(1024)
            print data
            self.incoming_parser(data)

# Class Name: WriteThread
class WriteThread (threading.Thread):
    def __init__(self, name, ssoc, condition, sendQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.ssoc = ssoc
        self.sendQueue = sendQueue
        self.condition = condition

    def run(self):
        while True:
            #self.condition.acquire()
            if self.sendQueue.qsize() > 0:
                queue_message = self.sendQueue.get()
                try:
                    temp = str(queue_message)
                    self.ssoc.send(str(queue_message))
                except socket.error:
                    self.ssoc.close()
                    break
            #else:
                #self.condition.wait()

            #self.condition.release()

class ClientDialog(QDialog):

    def __init__(self, sendQueue, screenQueue, sessionQueue, sitQueue, cardQueue):
        self.sendQueue = sendQueue
        self.screenQueue = screenQueue
        self.sessionQueue = sessionQueue
        self.sitQueue = sitQueue
        self.cardQueue = cardQueue

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
        self.vbox.setGeometry(QRect(10, 10, 600, 461))

        # Add a horizontal layout
        self.hbox = QHBoxLayout()

        # Add a vertical layout2
        self.vbox2 = QVBoxLayout()

        # The sender textbox
        self.sender = QLineEdit("", self)

        # The channel region
        self.channel = QTextBrowser()
        self.channel.setMinimumSize(QSize(480, 0))

        # The send button
        self.send_button = QPushButton('&Send')

        #Num cov
        self.numToCover = QLineEdit("", self)

        #Cover button
        self.close_button = QPushButton('&Close')

        #Cover button
        self.cover_button = QPushButton('&Cover')

        #Ready button
        self.ready_button = QPushButton('&Ready')

        # The session section
        self.sessionList = QListView()
        self.sessionList.setWindowTitle('Session List')

        # The situation section
        self.situationList = QListView()
        self.situationList.setWindowTitle('Situation List')

        # The myCard section
        self.myCardList = QListView()
        self.myCardList.setWindowTitle('Session List')

        # Connect the Go button to its callback
        self.send_button.clicked.connect(self.outgoing_parser)

        # Connect the Go button to its callback
        self.ready_button.clicked.connect(self.send_ready)

        # Connect the Go button to its callback
        self.close_button.clicked.connect(self.close_game)

        # Connect the Go button to its callback
        self.cover_button.clicked.connect(self.cover_num)

        self.myCard = []

        # Add the controls to the vertical layout
        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.sender)
        self.vbox.addWidget(self.send_button)
        self.hbox.addWidget(self.channel)
        self.hbox.addLayout(self.vbox2)
        self.vbox2.addWidget(self.sessionList)
        self.vbox2.addWidget(self.situationList)
        self.vbox2.addWidget(self.myCardList)
        self.vbox2.addWidget(self.numToCover)
        self.vbox2.addWidget(self.cover_button)
        self.vbox2.addWidget(self.ready_button)
        self.vbox2.addWidget(self.close_button)

        # start timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateChannelWindow)
        self.timer2 = QTimer()
        self.timer2.timeout.connect(self.updateSessionList)
        self.timer3 = QTimer()
        self.timer3.timeout.connect(self.updateSituationList)
        self.timer4 = QTimer()
        self.timer4.timeout.connect(self.updateMyCardList)

        # update every 10 ms
        self.timer.start(10)
        self.timer2.start(500)
        self.timer3.start(500)
        self.timer4.start(500)

        # Use the vertical layout for the current window
        self.setLayout(self.vbox)

    # use this to append new message to channel with timestamp
    def cprint(self, data):
        now = datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S')
        channel_msg = now + " " + data
        self.channel.append(channel_msg)

    def updateChannelWindow(self):
        if self.screenQueue.qsize() > 0:
            queue_message = self.screenQueue.get()
            self.cprint(queue_message)

    def updateSessionList(self,):
        if self.sessionQueue.qsize() > 0:
            queue_message = self.sessionQueue.get()
            self.sessionPrint(queue_message)

    def updateSituationList(self,):
        if self.sitQueue.qsize() > 0:
            queue_message = self.sitQueue.get()
            self.situationPrint(queue_message)

    def updateMyCardList(self,):
        if self.cardQueue.qsize() > 0:
            queue_message = self.cardQueue.get()
            self.cardPrint(queue_message)

    def cardPrint(self, card):
        model = QStandardItemModel(self.myCardList)

        for row in card:
            item = QStandardItem(row)
            model.appendRow(item)
            self.myCard.append(row.split("-"))

        self.myCardList.setModel(model)
        self.timer4.stop()
        self.myCardList.show()

    def uprint(self, sessions):
        model = QStandardItemModel(self.sessionList)

        for session in sessions:
            item = QStandardItem(str(session))
            model.appendRow(item)

        self.sessionList.setModel(model)
        self.sessionList.show()

    def sessionPrint(self, session):
        model = QStandardItemModel(self.sessionList)

        for ses in session:
            item = QStandardItem(ses)
            model.appendRow(item)

        self.sessionList.setModel(model)
        self.sessionList.show()


    def situationPrint(self, situation):
        model = QStandardItemModel(self.situationList)

        for sit in situation:
            item = QStandardItem(sit)
            model.appendRow(item)

        self.situationList.setModel(model)
        self.situationList.show()

    def outgoing_parser(self):
        data = self.sender.text()

        self.sendQueue.put(data)
        self.sender.clear()

    def send_ready(self):
        message = "RDY"
        self.sendQueue.put(message)

    def close_game(self):
        message = "QUI"
        self.sendQueue.put(message)

    def cover_num(self):
        num = self.numToCover.text()
        num = str(num)
        for row in self.myCard:
            i = 0
            for item in row:
                if item == num:
                    row[i] = "X"
                    break
                i += 1

        print self.myCard

    #Run the app and show the main form
    def run(self):
        self.show()
        self.qt_app.exec_()

# Connect to the server
ssoc = socket.socket()
host = "192.168.1.182"
port = 12345
ssoc.connect((host,port))

sendQueue = Queue.Queue()
readQueue = Queue.Queue()
screenQueue = Queue.Queue()
sessionQueue = Queue.Queue()
sitQueue = Queue.Queue()
cardQueue = Queue.Queue()

app = ClientDialog(sendQueue, screenQueue, sessionQueue, sitQueue, cardQueue)

condition = threading.Condition()

# start threads
rt = ReadThread("ReadThread", ssoc, condition, sendQueue, screenQueue, sessionQueue, sitQueue, cardQueue)
rt.start()
wt = WriteThread("WriteThread", ssoc, condition, sendQueue)
wt.start()

app.run()