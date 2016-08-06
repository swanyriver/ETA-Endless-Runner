#/usr/bin/python2.7
# references
# https://wiki.python.org/moin/TcpCommunication 
import sys
import socket
import cursesIO
from multiprocessing import Process, Pipe
from log import log
import networkKeys

#TODO currently breaksif newline entered first

def getUsersHandle():
   print("What would you like to your handle, it must be 10 characters or less")

   person = raw_input('Enter your name: ')
   #check if handle is less than 10 char
   if(len(person) > 10):
       print("error! requested handle is too long")
       person=getUsersHandle();

   #check if there are spaces in handle
   if(" " in person):
       print("There's a space in your username")
       person=getUsersHandle();
   return person

##-- MAIN --##
def main(argv):
    #specify host name and port number on the command line.
    TCP_IP = sys.argv[1] 
    TCP_PORT = int(sys.argv[2])  
    BUFFER_SIZE = 5000

    #--connect to server--#
    #create sock stream and connect  
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.settimeout(.2)

    name = getUsersHandle()
    s.sendall(networkKeys.ACTIONS.name + name + "\n")

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
