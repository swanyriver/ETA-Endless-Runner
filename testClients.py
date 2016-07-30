#/usr/bin/python2.7
# references
# https://wiki.python.org/moin/TcpCommunication 
import sys
import SocketServer
import socket
import cursesIO
from multiprocessing import Process, Pipe
from log import log
import random
import time

#TODO currently breaksif newline entered first

##-- Functions --##

#user is either vertical or horizontal  
def getUserInput(user):
    userInput = raw_input(user+'>')
    return userInput

##-- MAIN --##
def main(argv):
    #specify host name and port number on the command line.
    TCP_IP = sys.argv[1] 
    TCP_PORT = int(sys.argv[2])  
    BUFFER_SIZE = 1024
    quit="\quit"

    #--connect to server--#
    #create sock stream and connect  
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.settimeout(.2)

    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s2.connect((TCP_IP, TCP_PORT))
    s2.settimeout(.2)

    actions = "wasd"

    while True:
        time.sleep(.25)
        socketASends = random.choice([True, False])
        socketBSends = random.choice([True, False])

        if socketASends:
            s.sendall(random.choice(actions) + "\n")
        if socketBSends:
            s.sendall(random.choice(actions) + "\n")

        try:
            updateFromServer = s.recv(BUFFER_SIZE)
            if updateFromServer:
                print "client a recieved: ", updateFromServer
        except socket.timeout:
            pass

        try:
            updateFromServer = None
            updateFromServer = s2.recv(BUFFER_SIZE)
            if updateFromServer:
                print "client b recieved: ", updateFromServer
        except socket.timeout:
            pass



    ############################################################
    #### curses process has ended ##############################
    ############################################################

    #send termination message s.send(MESSAGE.encode())
    log("(NET): closing connection")
    #close connection
    s.close()

#--MAIN--#
if __name__ == "__main__":
    main(sys.argv)
