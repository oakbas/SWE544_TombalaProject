#FileName: TombalaServer.py
#Author : Ozlem Akbas
#Description : SWE544 Course Project for Tombala Multi Player Game

import sys
import socket
import threading
import Queue

class ClientThread (threading.Thread):
    def __init__(self, name, csoc, threadQueue, readQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.nickname = ""
        self.threadQueue = threadQueue
        self.readQueue = readQueue

    def incoming_parser(self, data):
        rest = data[4:]     #get the rest of the message, no problem even if data < 4

        #The case, user has already logged in
        if self.nickname:
            #ToDo: Implement All Protocol Messages
            #The case, message has less than three-character length
            if len(data) < 3:
                response = "ERR"
                self.csoc.send(response)
                return

            #The case, command root is more than three characters
            if len(data) > 3 and not data[3] == " ":
                response = "ERR"
                self.csoc.send(response)
                return

        #The case, user has not logged in yet
        else:
            #The case, message has less than three-character length
            if len(data) < 3:
                response = "ERL"
                self.csoc.send(response)
                return
            elif data[0:3] == "USR":
                self.nickname = rest
                #ToDo: nickname validity check(existing or typo error)
                response = "HEL " + rest
                self.csoc.send(response)

            #ToDo: Log Case

            else:
                response = "ERL"
                self.csoc.send(response)

    def run(self):
        while True:
            data = self.csoc.recv(1024)
            self.incoming_parser(data)

#Main Thread
ssoc = socket.socket()
host = socket.gethostname()
print host
port = 12345
ssoc.bind((host, port))
ssoc.listen(5)
sendQueue = Queue.Queue()
readQueue = Queue.Queue()
while True:
    csoc, addr = ssoc.accept()     # Establish connection with client.
    print 'Got connection from', addr
    csoc.send('Thank you for connecting!')
    rt = ClientThread("ClientThread", csoc, sendQueue, readQueue)
    rt.start()
ssoc.close()
