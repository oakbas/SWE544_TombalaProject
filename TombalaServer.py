#FileName: TombalaServer.py
#Author : Ozlem Akbas
#Description : SWE544 Course Project for Tombala Multi Player Game

import sys
import socket
import threading
import Queue

class ClientThread (threading.Thread):
    def __init__(self, threadId, usernameList, csoc, threads):
        threading.Thread.__init__(self)
        self.thredId = threadId
        self.csoc = csoc
        self.nickname = ""
        self.threads = threads
        self.threads.append(self)
        self.exitFlag = 0

    def incoming_parser(self, data):

        #The case, user has already logged in
        if self.nickname:
            #Todo: If check a session is start
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

            rest = data[4:]     #get the rest of the message, no problem even if data < 4

            #The case, communication ends
            if data[0:3] == "QUI":
                if len(rest) > 0:
                    response = "ERR"
                    self.csoc.send(response)
                    return
                #Todo: Main thread update, usernamelist update
                response = "BYE " + self.nickname
                self.csoc.send(response)
                threads.remove(self)
                self.exitFlag = 1
                return

            #The case, getting session list request
            if data[0:3] == "LSS":
                if len(rest) > 0:
                    response = "ERR"
                    self.csoc.send(response)
                    return
                #Todo: get session list dictionary
                sessionList = "none"
                response = "LSA " + sessionList
                self.csoc.send(response)

            #The case, creating new session request
            if data[0:3] == "CRT":
                if len(rest) > 0:
                    response = "ERR"
                    self.csoc.send(response)
                    return
                #Todo: get session list dictionary
                #Todo: create new session id and add to dictinary and add this in response
                response = "CAC "

            #The case, joining existing session request
            if data[0:3] == "JNS":
                if len(rest) == 0:
                    response = "ERR"
                    self.csoc.send(response)
                #Todo: check if the game started
                #Todo: else search sessionId in the dictionary and check it, send response according to it
                response = "REJ"
                self.csoc.send(response)
                response = "ADD "
                self.csoc.send(response)

        #The case, user has not logged in yet
        else:
            #The case, message has less than three-character length
            if len(data) < 3:
                response = "ERL"
                self.csoc.send(response)
                return

            #The case, command root is more than three characters
            if len(data) > 3 and not data[3] == " ":
                response = "ERL"
                self.csoc.send(response)
                return

            rest = data[4:]     #get the rest of the message, no problem even if data < 4

            #The case, client registration
            if data[0:3] == "USR":
                self.nickname = rest
                #ToDo: nickname validity check(existing or typo error)
                response = "HEL " + rest
                self.csoc.send(response)

            #The case, client log in
            elif data[0:3] == "LOG":
                if rest in usernameList:
                    response = "HEL " + rest
                    self.csoc.send(response)
                #ToDo: check this user is currently in the system
                else:
                    response = "REJ"
                    self.csoc.send(response)
            else:
                response = "ERL"
                self.csoc.send(response)

    def run(self):
        while True:
            data = self.csoc.recv(1024)
            data = data.rstrip('\r\n')
            self.incoming_parser(data)
            if self.exitFlag == 1:
                self.csoc.close()
                return

#Main Thread
ssoc = socket.socket()
host = socket.gethostname()
port = 12345
ssoc.bind((host, port))
threadId = -1
threads = []
usernameList = []
ssoc.listen(5)

sendQueue = Queue.Queue() #Todo: Async case

#Listen Socket
while True:
    csoc, addr = ssoc.accept()     # Establish connection with client.
    print 'Got connection from', addr
    csoc.send('Thank you for connecting!')
    threadId += 1
    ct = ClientThread(threadId, usernameList, csoc, threads)
    ct.start()
    ct.join()

ssoc.close()
