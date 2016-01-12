#FileName: TombalaServer.py
#Author : Ozlem Akbas
#Description : SWE544 Course Project for Tombala Multi Player Game

import sys
import socket
import threading
import Queue
import random
import time

#SessionNum = 0
gameSessionId = ""

# Class Name: GameThread
# Description : This class for game states in the tombala
class GameThread (threading.Thread):
    def __init__(self, name, condition, sessionDict, gameSessionId, sendQueue):
        threading.Thread.__init__(self)
        self.name
        self.condition = condition
        self.sessionDict = sessionDict
        self.gameState = 0
        self.gameSessionId = gameSessionId
        self.sendQueue = sendQueue
        self.counter1 = 0
        self.counter2 = 0

    def createCards(self):
        tombalaCardList = []
        tombalaCard0 = [['1','20','40','64','71'],['10','30','56','79','88'],['2','23','46','68','87']]
        tombalaCardList.append(tombalaCard0)
        tombalaCard1 = [['7','26','46','63','72'],['15','34','56','76','86'],['5','22','48','62','89']]
        tombalaCardList.append(tombalaCard1)
        tombalaCard2 = [['8','10','36','50','71'],['15','26','40','60','83'],['2','21','39','56','74']]
        tombalaCardList.append(tombalaCard2)
        tombalaCard3 = [['1','25','44','63','74'],['20','40','54','85','86'],['7','26','51','69','87']]
        tombalaCardList.append(tombalaCard3)
        tombalaCard4 = [['1','25','45','63','71'],['15','39','53','79','82'],['3','29','48','65','90']]
        tombalaCardList.append(tombalaCard4)
        tombalaCard5 = [['2','23','45','64','71'],['18','32','58','78','80'],['5','25','49','69','86']]
        tombalaCardList.append(tombalaCard5)
        tombalaCard6 = [['2','23','43','60','74'],['12','32','53','79','80'],['5','20','49','69','84']]
        tombalaCardList.append(tombalaCard6)
        tombalaCard7 = [['7','23','41','63','89'],['12','24','44','65','78'],['5','16','32','56','90']]
        tombalaCardList.append(tombalaCard7)
        tombalaCard8 = [['3','12','30','53','73'],['16','21','41','61','87'],['9','24','35','57','70']]
        tombalaCardList.append(tombalaCard8)
        tombalaCard9 = [['9','12','34','54','73'],['19','24','44','66','84'],['6','24','35','57','70']]
        tombalaCardList.append(tombalaCard9)

        random.shuffle(tombalaCardList)
        return tombalaCardList

    def randomNumber(self):

        luckyNum = range(1,91,1)
        random.shuffle(luckyNum)

        #Test data
        #luckyNum = [1,20,40,64,71,10,30,56,79,88,2,23,46,68,87,100]
        return luckyNum

    def run(self):
        global gameStart
        luckNumbers = []
        nextNumIndex = 0
        while True:
            #The state, to control if a session meets requirement

            #The state waiting for sessions
            if self.gameState == 0:
                condition.acquire()
                for session in self.sessionDict:
                    #Game shall not start less than 3 people
                    if len(self.sessionDict[session]) >= 3:
                        self.gameSessionId = session
                        response = "STR " + session
                        messageType = 1
                        message = Message(messageType,response)
                        self.sendQueue.put(message)
                        self.gameState = 1
                condition.release()
                time.sleep(5)

            #The state waiting for STA message from gamer to start game
            elif self.gameState == 1:
                result = True
                condition.acquire()
                for gamer in self.sessionDict[self.gameSessionId]:
                    result &= gamer.inGame
                condition.release()
                if result:
                    self.counter1 = 0
                    self.gameState = 2
                    gameStart = True
                    luckNumbers = self.randomNumber()
                    nextNumIndex = 0
                else:
                    time.sleep(5)
                    self.counter1 += 1
                    if self.counter1 == 5:
                        self.gameState = 4

            #The state to give cards
            elif self.gameState == 2:
                cardList = self.createCards()
                i = 0
                messageBody = ""
                condition.acquire()
                for gamer in self.sessionDict[self.gameSessionId]:
                    gamer.card = cardList[i]
                    i += 1
                    messageBody += gamer.nickname + ":"
                    for row in gamer.card:
                        messageBody += '-'.join(row)
                        messageBody += ","
                    messageBody = messageBody[:-1]
                    messageBody += ";"
                condition.release()
                messageBody = messageBody[:-1]

                condition.acquire()
                for gamer in self.sessionDict[self.gameSessionId]:
                    response = "APC " + messageBody
                    messageType = 0
                    message = Message(messageType,response, gamer)
                    self.sendQueue.put(message)
                condition.release()
                self.gameState = 3

            #The state of playing the game
            elif self.gameState == 3:
                result = True
                condition.acquire()
                for gamer in self.sessionDict[self.gameSessionId]:
                    result &= gamer.readyFlag
                condition.release()
                if result:
                    self.counter2 = 0
                    lck = luckNumbers[nextNumIndex]
                    nextNumIndex += 1
                    response = "NMB " + str(lck)
                    messageType = 0
                    message = Message(messageType,response)
                    global gameSituation
                    gameSituation = ""
                    condition.acquire()
                    for gamer in self.sessionDict[self.gameSessionId]:
                        gamer.coverNum(str(lck))

                        if not gamer.fcn:
                            gameSituation += gamer.nickname + ",0"

                        if gamer.fcn:
                        #elif not gamer.sc and gamer.fc:
                            gameSituation += gamer.nickname + ",1"

                        if gamer.scn:
                        #elif gamer.sc and gamer.fc:
                            gameSituation += gamer.nickname + ",2"

                        if gamer.tmbn:
                            gameSituation += gamer.nickname + ",3"
                            response = "SAY" + gamer.nickname + " won !!!" + '\n' + "Get ready for next round !!!"
                            messageType = 1
                            message = Message(messageType,response)
                            self.gameState = 4

                        gameSituation += ":"

                        message = Message(messageType,response,gamer)
                        gamer.readyFlag = False
                        self.sendQueue.put(message)
                    condition.release()
                else:
                    time.sleep(2)
                    self.counter2 += 1
                    if self.counter2 == 20:
                        self.gameState = 4

            #Finalizing or cleaning state
            elif self.gameState == 4:
                self.gameState = 0
                gameStart = False
                self.counter1 = 0
                self.counter2 = 0
                condition.acquire()
                for gamer in self.sessionDict[self.gameSessionId]:
                    gamer.removeFromSession()
                self.gameSessionId = ""
                condition.release()
                response = "DRP " + self.gameSessionId
                messageType = 1
                message = Message(messageType, response)
                condition.acquire()
                self.sessionDict.pop(self.gameSessionId, None)
                condition.release()

                print response
                self.sendQueue.put(message)

# Class Name: ClientThread
# Description : This class for threads of new connected client
class ClientThread (threading.Thread):
    def __init__(self, threadId, condition, usernameList, csoc, threads, sendQueue, sessionDict, gameSessionId, card):
        threading.Thread.__init__(self)
        self.condition = condition
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
        self.sessionTimer = sessionTimer
        self.inGame = False
        self.readyFlag = False
        self.fc = False
        self.fcn = False
        self.sc = False
        self.scn = False
        self.tmb = False
        self.tmbn = False
        self.removed = False
        self.gameSessionId = gameSessionId
        self.card = card
        self.gameSituation = gameSituation

    def removeFromSession(self):
        if not self.removed:
            self.removed = True
            try:
                self.sessionDict[self.joinedSession].remove(self)
            except ValueError:
                pass
            if not self.sessionDict[self.joinedSession]:
                self.sessionDict.pop(self.joinedSession, None)
            self.joinedSession = ""

    def coverNum(self, num):
        for row in self.card:
            i = 0
            for item in row:
                if item == num:
                    row[i] = '0'
                i += 1
        self.checkCnk()

    def checkCnk(self):
        cnkCounter = 0
        for row in self.card:
            if ''.join(row) == "00000":
                cnkCounter +=1
        #Check cinko 1
        if cnkCounter == 1:
            self.fc = True
        #Check cinko 2
        elif cnkCounter == 2:
            self.sc = True
        #Check Tombala
        elif cnkCounter == 3:
            self.tmb = True
        else:
            self.fc = False
            self.sc = False
            self.tmb = False

    def incoming_parser(self, data):
        global SessionNum
        #The case, user has already logged in
        if self.nickname:

            #The case game has started
            global gameStart
            if gameStart:

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
                    if len(rest) > 0:
                        response = "ERR"
                        self.csoc.send(response)
                        return
                    self.readyFlag = True

                #The case, communication ends
                if data[0:3] == "QUI":
                    if len(rest) > 0:
                        response = "ERR"
                        self.csoc.send(response)
                        return
                    response = "BYE " + self.nickname
                    self.csoc.send(response)
                    self.exitFlag = 1
                    return

                #The case, cinko request
                if data[0:3] == "CNK":
                    if len(rest) == 0:
                        response = "ERR"
                        self.csoc.send(response)
                        return

                    #Cinko check
                    if rest[0] == "1":
                        if self.fc:
                            self.fcn = True
                            response = "CNA"
                            self.csoc.send(response)
                        else:
                            response = "CNR"
                            self.csoc.send(response)
                    elif rest[0] == "2":
                        if self.sc:
                            self.scn = True
                            response = "CNA"
                            self.csoc.send(response)
                        else:
                            response = "CNR"
                            self.csoc.send(response)
                    else:
                        response = "CNR"
                        self.csoc.send(response)

                    self.readyFlag = True

                #The case, tombala request
                if data[0:3] == "TBL":
                    if len(rest) == 0:
                        response = "ERR"
                        self.csoc.send(response)
                        return
                    #Tombala check
                    if self.tmb:
                        self.tmbn = True
                        response = "TBA"
                    else:
                        response = "TBR"

                    #General message for accept
                    self.csoc.send(response)

                #The case, situation information request
                if data[0:3] == "QRY":
                    if len(rest) > 0:
                        response = "ERR"
                        self.csoc.send(response)
                        return
                    global gameSituation
                    response = "INF " + gameSituation[:-1]
                    self.csoc.send(response)

            #The case, game has not started
            else:
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
                elif data[0:3] == "CRS":
                    if len(rest) > 0:
                        response = "ERR"
                        self.csoc.send(response)
                        return
                    #Create new session
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
                        self.removed = False
                        self.csoc.send(response)

                #The case, joining existing session request
                elif data[0:3] == "JNS":
                    if len(rest) == 0:
                        response = "ERR"
                        self.csoc.send(response)
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
                                    self.joinedSession = sessionID
                                    response = "JNA " + sessionID
                                    self.removed = False
                                    self.csoc.send(response)

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
                        condition.acquire()
                        self.removeFromSession()
                        condition.release()
                    else:
                        response = "QGR"
                        self.csoc.send(response)

                #The case ready to game
                elif data[0:3] == "STA":
                    if len(rest) > 0:
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
                else:
                    response = "REJ"
                    self.csoc.send(response)

            #If not registered user
            else:
                response = "ERL"
                self.csoc.send(response)

    def run(self):
        global gameStart
        while True:
            try:
                data = self.csoc.recv(1024)
                data = data.rstrip('\r\n')

                #If the player is not in the game and game start, send OUT
                if gameStart and not self.inGame:
                    self.csoc.send("OUT")
                else:
                    condition.acquire()
                    self.incoming_parser(data)
                    condition.release()
                    #Quit with QUI command
                    if self.exitFlag == 1:
                        condition.acquire()
                        self.removeFromSession()
                        condition.release()
                        self.threads.remove(self)
                        response = "SAY " + self.nickname + " is disconnected"
                        messageType = 1
                        message = Message(messageType,response)
                        self.sendQueue.put(message)
                        self.csoc.close()
                        return
            except socket.error:
                condition.acquire()
                self.removeFromSession()
                condition.release()
                self.threads.remove(self)
                response = "SAY " + self.nickname + " is disconnected"
                messageType = 1
                message = Message(messageType, response)
                self.sendQueue.put(message)
                self.csoc.close()
                return

# Class Name: WriteThread
# Description : This class for sending async queue messages
class WriteThread (threading.Thread):
    def __init__(self, condition, name, usernameList, threads, sendQueue, sessionDict):
        threading.Thread.__init__(self)
        self.name = name
        self.threads = threads
        self.sendQueue = sendQueue
        self.condition = condition
        self.sessionDict = sessionDict

    def run(self):
        while True:
            if self.sendQueue.qsize() > 0:
                queue_message = self.sendQueue.get()
                #General Message
                if queue_message.type == 1:
                    temp = queue_message.message
                    for clientThread in self.threads:
                        if clientThread.nickname:
                            try:
                                clientThread.csoc.send(temp)
                            except socket.error:
                                condition.acquire()
                                clientThread.removeFromSession()
                                condition.release()
                                clientThread.csoc.close()
                                break
                else:
                    temp = queue_message.message
                    try:
                        queue_message.receiver.csoc.send(temp)
                    except socket.error:
                        condition.acquire()
                        queue_message.receiver.removeFromSession()
                        condition.release()

                        queue_message.receiver.csoc.close()
                        break

class Message(object):
    def __init__(self, type, messagebody, receiver = None):
        if receiver:
            self.receiver = receiver
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

global SessionNum
SessionNum = 0

global gameStart
gameStart = False

#Game session init
sessionDict = {}
sessionTimer = {}

card = [[],[],[]]

gameSituation = ""
condition = threading.Condition()

gt = GameThread("GameThread", condition, sessionDict, gameSessionId, sendQueue)
gt.start()

wt = WriteThread("WriteThread", condition, usernameList, threads, sendQueue, sessionDict)
wt.start()

ssoc.listen(5)

#Listen Socket
while True:
    csoc, addr = ssoc.accept()     # Establish connection with client.
    print 'Got connection from', addr
    csoc.send("SAY " + "Thank you for connecting!")
    threadId += 1
    ct = ClientThread(threadId, condition, usernameList, csoc, threads, sendQueue, sessionDict, gameSessionId, card)
    ct.start()

ssoc.close()
