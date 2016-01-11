#FileName: TombalaServer.py
#Author : Ozlem Akbas
#Description : SWE544 Course Project for Tombala Multi Player Game

import sys
import socket
import threading
import Queue
import random

SessionNum = 0
gameStart = ""

def createCards():
    tombalaCardList = []
    tombalaCard0 = [[1,20,40,64,71],[10,30,56,79,88],[2,23,46,68,87]]
    tombalaCardList.append(tombalaCard0)
    tombalaCard1 = [[7,26,46,63,72],[15,34,56,76,86],[5,22,48,62,89]]
    tombalaCardList.append(tombalaCard1)
    tombalaCard2 = [[8,10,36,50,71],[15,26,40,60,83],[2,21,39,56,74]]
    tombalaCardList.append(tombalaCard2)
    tombalaCard3 = [[1,25,44,63,74],[20,40,54,85,86],[7,26,51,69,87]]
    tombalaCardList.append(tombalaCard3)
    tombalaCard4 = [[1,25,45,63,71],[15,39,53,79,82],[3,29,48,65,90]]
    tombalaCardList.append(tombalaCard4)
    tombalaCard5 = [[2,23,45,64,71],[18,32,58,78,80],[5,25,49,69,86]]
    tombalaCardList.append(tombalaCard5)
    tombalaCard6 = [[2,23,43,60,74],[12,32,53,79,80],[5,20,49,69,84]]
    tombalaCardList.append(tombalaCard6)
    tombalaCard7 = [[7,23,41,63,89],[12,24,44,65,78],[5,16,32,56,90]]
    tombalaCardList.append(tombalaCard7)
    tombalaCard8 = [[3,12,30,53,73],[16,21,41,61,87],[9,24,35,57,70]]
    tombalaCardList.append(tombalaCard8)
    tombalaCard9 = [[9,12,34,54,73],[19,24,44,66,84],[9,24,35,57,70]]
    tombalaCardList.append(tombalaCard9)

    return tombalaCardList

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
        self.readyFlag = False
        self.sessionTimer = sessionTimer
        self.inGame = False
        global gameStart

    def incoming_parser(self, data):

        #Todo: Before csoc.send check csoc is connected
        #The case, user has already logged in
        if self.nickname:
            #The case game has started
            if gameStart and self.inGame:
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

                #The case, gamer ready for new number
                if data[0:3] == "RDY":
                    if len(rest) == 0:
                        response = "ERR"
                        self.csoc.send(response)
                        return
                    #Todo: Keep game thread (includes card, situation, ready for next)
                    self.readyFlag = True

                #The case, cinko request
                if data[0:3] == "CNK":
                    if len(rest) == 0:
                        response = "ERR"
                        self.csoc.send(response)
                        return
                    #Todo: Cinko check
                    response = "CNA"
                    response = "CNR"

                #The case, tombala request
                if data[0:3] == "TBL":
                    if len(rest) == 0:
                        response = "ERR"
                        self.csoc.send(response)
                        return
                    #Todo: Tombala check
                    response = "TBA"
                    response = "TBR"

                #The case, tombala request
                if data[0:3] == "TBL":
                    if len(rest) > 0:
                        response = "ERR"
                        self.csoc.send(response)
                        return
                    #Todo: Tombala check
                    response = "TBA"
                    response = "TBR"

                #The case, situation information request
                if data[0:3] == "QRY":
                    if len(rest) > 0:
                        response = "ERR"
                        self.csoc.send(response)
                        return
                    #Todo: Take situation from gameThread
                    response = "INF"

            #The case, game has not started
            else:
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
                        response = "CSR"
                        self.csoc.send(response)
                    else:
                        SessionNum += 1
                        sessionUserList = []
                        sessionUserList.append(self)
                        dkey = str(SessionNum)
                        self.joinedSession = dkey
                        self.sessionDict[dkey] = sessionUserList
                        response = "CSA " + dkey
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
                        response = "JNR"
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
                                    response = "JNR"
                                    self.csoc.send(response)
                                    return
                                else:
                                    self.sessionDict[sessionID].append(self)
                                    response = "JNA " + sessionID
                                    self.csoc.send(response)
                                    self.joinedSession = sessionID
                                    if len(sessionDict[sessionID]) == 2:
                                        gameStart = sessionID
                                        response = "SAY " + "Ready for start message"
                                        messageType = 1
                                        message = Message(messageType,response)
                                        self.sendQueue.put(message)

                        #Wrong sessionID
                        else:
                            response = "JNR"
                            self.csoc.send(response)

                #The case, exit from session requests
                elif data[0:3] == "QGM":
                    if len(rest) > 0:
                        response = "ERR"
                        self.csoc.send(response)
                        return
                    #Not registered a session
                    if self.joinedSession:
                        response = "QGA"
                        self.csoc.send(response)
                        for self.joinedSession in self.sessionDict:
                            self.sessionDict[self.joinedSession].remove(self)
                            if not self.sessionDict[self.joinedSession]:
                                self.sessionDict.pop(self.joinedSession,None)
                            break
                        self.joinedSession = ""
                    else:
                        response = "QGR"
                        self.csoc.send(response)

                #The case ready to game
                elif data[0:3] == "STA":
                    if len(rest) == 0:
                        response = "ERR"
                        self.csoc.send(response)
                        return
                    self.inGame = True
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
    def __init__(self, name, usernameList, threads, sendQueue, sessionDict):
        threading.Thread.__init__(self)
        self.name = name
        self.threads = threads
        self.sendQueue = sendQueue
        self.sessionDict = sessionDict
        global gameStart

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

                    if gameStart:
                        cards = createCards()
                        cards = random.shuffle(cards)

                        #Threads who are playing in the game
                        gameThread = self.sessionDict[gameStart]
                        self.sessionDict = {}

                        for clientThread in gameThread:
                            clientThread.csoc.send("STR " + gameStart)


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

#Game session init
sessionDict = {}
sessionTimer = {}

gameThread = []

#Async message (Todo: thread wait)
wt = WriteThread("WriteThread", usernameList, threads, sendQueue, sessionDict)
wt.start()


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
