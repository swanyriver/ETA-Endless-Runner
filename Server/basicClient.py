#/usr/bin/python2.7
# references
# https://wiki.python.org/moin/TcpCommunication 
import sys
import SocketServer
import socket
import threading

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
    quit="quit"

    #--connect to server--#
    #create sock stream and connect  
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.setblocking(0)

    userHandle="UserName"#TODO determine if which Client

    #get initial input
    MESSAGE = getUserInput(userHandle)

    #while the user hasn't quit send and receive msgs
    while(MESSAGE != quit):
        response=""
        try:
            s.sendall(MESSAGE)
            response = s.recv(1024)
            print "Received: {}".format(response)
        except:
            if response != "":
                pass
        MESSAGE = getUserInput(userHandle)

    print("closing connection")
    #close connection
    s.close()

#--MAIN--#
if __name__ == "__main__":
    main(sys.argv)
