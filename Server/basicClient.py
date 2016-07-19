#/usr/bin/python2.7
# references
# https://wiki.python.org/moin/TcpCommunication 
import sys
import SocketServer
import socket

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

    userHandle="vertical"
    #TODO determine if verticalClient or horizontalClient

    #get initial input
    MESSAGE = getUserInput(userHandle)

    #while the user hasn't quit send and receive msgs
    while(MESSAGE != quit):

        s.sendall(MESSAGE)
        response = s.recv(1024)
        print "Received: {}".format(response)

        #TODO REMOVE
        #send message
        #s.send(MESSAGE.encode())
        #data = s.recv(BUFFER_SIZE).decode()
        #sys.stdout.write(data)

        #allow user to input text
        #TODO replace write with sending data to curses client

        MESSAGE = getUserInput(userHandle)

    #send termination message s.send(MESSAGE.encode())
    print("closing connection")
    #close connection
    s.close()

#--MAIN--#
if __name__ == "__main__":
    main(sys.argv)
