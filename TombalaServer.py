#FileName: TombalaServer.py
#Author : Ozlem Akbas
#Description : SWE544 Course Project for Tombala Multi Player Game

import sys
import socket
import threading
import Queue

SessionNum = 0

class ClientThread (threading.Thread):
    def __init__(self, threadId, usernameList, csoc, threads, sendQueue, sessionDict):
        threading.Thread.__init__(self)
        self.thredId = threadId
        self.usernameList = usernameList
        self.csoc = csoc
        self.nickname = ""
        self.threads = threads
        self.threads.append(self)
        self.exitFlag = 0
        self.sendQueue = sendQueue
        self.sessionDict = sessionDict
        self.joinedSession = ""

    def incoming_parser(self, data):

        #Todo: Before csoc.send check csoc is connected

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
                self.exitFlag = 1
                return

            #The case, getting session list request
            elif data[0:3] == "LSS":
                if len(rest) > 0:
                    response = "ERR"
                    self.csoc.send(response)
                    return
                #Todo: get session list dictionary
                sessionMessage = " "
                for session in self.sessionDict:
                    sessionMessage += session + ":"
                    for thread in self.sessionDict[session]:
                        sessionMessage += thread.nickname + ','
                    sessionMessage = sessionMessage[:-1] + ";"
                sessionMessage = sessionMessage[:-1]
                response = "LSA" + sessionMessage
                self.csoc.send(response)

            #The case, creating new session request
            elif data[0:3] == "CRT":
                if len(rest) > 0:
                    response = "ERR"
                    self.csoc.send(response)
                    return
                #Create new session
                global SessionNum
                if self.joinedSession:
                    response = "CRJ"
                    self.csoc.send(response)
                else:
                    SessionNum += 1
                    sessionUserList = []
                    sessionUserList.append(self)
                    dkey = str(SessionNum)
                    self.joinedSession = dkey
                    self.sessionDict[dkey] = sessionUserList
                    response = "CAC " + dkey
                    self.csoc.send(response)

            #The case, joining existing session request
            elif data[0:3] == "JNS":
                if len(rest) == 0:
                    response = "ERR"
                    self.csoc.send(response)
                #Todo: check if the game started
                #Todo: else search sessionId in the dictionary and check it, send response according to it
                splitted = rest.split(":")
                #Wrong type of message
                if len(splitted) != 2:
                    response = "REJ"
                    self.csoc.send(response)
                    return
                else:
                    sessionID = splitted[0]
                    sentName = splitted[1]
                    if sessionID in self.sessionDict:
                        #Wrong username check
                        if sentName == self.nickname:
                            #Check if the user has already joined
                            if self.joinedSession:
                                response = "REJ"
                                self.csoc.send(response)
                                return
                            else:
                                self.sessionDict[sessionID].append(self)
                                response = "ADD " + sessionID
                                self.csoc.send(response)
                    #Wrong sessionID
                    else:
                        response = "REJ"
                        self.csoc.send(response)
            else:
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

            #The case, command root is more than three characters
            if len(data) > 3 and not data[3] == " ":
                response = "ERL"
                self.csoc.send(response)
                return

            rest = data[4:]     #get the rest of the message, no problem even if data < 4

            #The case, client registration
            if data[0:3] == "USR":
                #ToDo: nickname validity check(existing or typo error)
                if rest in self.usernameList:
                    response = "REJ " + self.nickname
                    self.csoc.send(response)
                    self.exitFlag = 1
                else:
                    self.nickname = rest
                    self.usernameList.append(self.nickname)
                    response = "HEL " + rest
                    self.csoc.send(response)
                    response = "SAY " + self.nickname + " is connected"
                    messageType = 1
                    message = Message(messageType,response)
                    self.sendQueue.put(message)

            #The case, client log in
            elif data[0:3] == "LOG":
                if rest in self.usernameList:
                    self.nickname = rest
                    response = "HEL " + rest
                    self.csoc.send(response)
                    response = "SAY " + self.nickname + " is connected"
                    messageType = 1
                    message = Message(messageType,response)
                    self.sendQueue.put(message)
                #ToDo: check this user is currently in the system
                else:
                    response = "REJ"
                    self.csoc.send(response)
            else:
                response = "ERL"
                self.csoc.send(response)

    def run(self):
        while True:
            try:
                data = self.csoc.recv(1024)
                data = data.rstrip('\r\n')
                self.incoming_parser(data)
                if self.exitFlag == 1:
                    threads.remove(self)
                    response = "SAY " + self.nickname + " is disconnected"
                    messageType = 1
                    message = Message(messageType,response)
                    self.sendQueue.put(message)
                    self.csoc.close()
                    return
            except socket.error:
                threads.remove(self)
                response = "SAY " + self.nickname + " is disconnected"
                messageType = 1
                message = Message(messageType,response)
                self.sendQueue.put(message)
                self.csoc.close()
                return


class WriteThread (threading.Thread):
    def __init__(self, name, usernameList, threads, sendQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.threads = threads
        self.sendQueue = sendQueue

    def run(self):
        while True:
            if self.sendQueue.qsize() > 0:
                queue_message = self.sendQueue.get()
                #General Message
                if queue_message.type == 1:
                    temp = queue_message.message
                    for clientThread in threads:
                        if clientThread.nickname:
                            try:
                                clientThread.csoc.send(temp)
                            #Todo: Custom message(session messages)
                            except socket.error:
                                self.csoc.close()
                                break

class Message(object):
    def __init__(self, type, messagebody):
        self.type = type    #type = 1; send to all, type=0; custom
        self.message = messagebody

#Main Thread
ssoc = socket.socket()
host = socket.gethostname()
port = 12345
ssoc.bind((host, port))
threadId = -1
threads = []
usernameList = []
sendQueue = Queue.Queue()

#Async message (Todo: thread wait)
wt = WriteThread("WriteThread", usernameList, threads, sendQueue)
wt.start()

#Game session init
sessionDict = {}

ssoc.listen(5)

#Listen Socket
while True:
    csoc, addr = ssoc.accept()     # Establish connection with client.
    print 'Got connection from', addr
    csoc.send('Thank you for connecting!')
    threadId += 1
    ct = ClientThread(threadId, usernameList, csoc, threads, sendQueue, sessionDict)
    ct.start()

ssoc.close()
