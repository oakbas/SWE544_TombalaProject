#FileName: TombalaServer.py
#Author : Ozlem Akbas
#Description : SWE544 Course Project for Tombala Multi Player Game

import sys
import socket
import threading
import Queue

#Main Thread

ssoc = socket.socket()
host = socket.gethostname()
print host
port = 12345
ssoc.bind((host, port))
ssoc.listen(5)
while True:
    c, addr = ssoc.accept()     # Establish connection with client.
    print 'Got connection from', addr
    c.send('Thank you for connecting!')
    c.close()

