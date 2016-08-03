#/usr/bin/python2.7
# references
# https://wiki.python.org/moin/TcpCommunication 
import sys
import socket
import cursesIO
from multiprocessing import Process, Pipe
from log import log

#TODO currently breaksif newline entered first


##-- MAIN --##
def main(argv):
    #specify host name and port number on the command line.
    TCP_IP = sys.argv[1] 
    TCP_PORT = int(sys.argv[2])  
    BUFFER_SIZE = 1024

    #--connect to server--#
    #create sock stream and connect  
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.settimeout(.2)

    userHandle="vertical"
    #TODO determine if verticalClient or horizontalClient

    ############################################################
    ####  Start curses process #################################
    ############################################################
    cursesEnd, networkEnd = Pipe(duplex=True)
    cursesProcess = Process(target=cursesIO.cursesEngine, args=(cursesEnd,))
    cursesProcess.start()

    while cursesProcess.is_alive():

        #get messages from curses
        if networkEnd.poll():
            msg = networkEnd.recv()
            log("(NET MSG-FROM-CURSES):" + str(type(msg)) + str(msg) + "\n")

            #todo megan,  add handler tag?
            #send curses message to server
            s.sendall(msg + "\n")

        #get update from server
        try:
            updateFromServer = s.recv(BUFFER_SIZE)
            updateFromServer = updateFromServer.decode()
            log("(NET MSG-TO-CURSES):" + updateFromServer + "\n")
            #send network update to cureses
            networkEnd.send(updateFromServer)
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
