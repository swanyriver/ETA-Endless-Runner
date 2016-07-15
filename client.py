#/usr/bin/python2.7
# references
# https://wiki.python.org/moin/TcpCommunication
import sys
import socket
from multiprocessing import Process, Pipe
import cursesIO

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

    #set non blocking mode for socket
    # very aggressive raises error immediately, check for socket.error exception
    #s.setblocking(0)
    #will alternate between sending messages and recieving with socket.timeout exception
    s.settimeout(.2)


    userHandle="vertical"
    #TODO determine if verticalClient or horizontalClient

    # network connection and other set up complete
    # start curses engine with in and out network connections
    sendPipe, cursesIn = Pipe()
    recPipe, cursesOut = Pipe()
    cursesProcess = Process(target=cursesIO.cursesEngine, args=(cursesOut, cursesIn))
    cursesProcess.start()

    MESSAGE = None
    messageSendAttempts = 0

    #while the user hasn't quit send and receive network msgs
    while(cursesProcess.is_alive()):
        #check for input from user and send to server
        if MESSAGE is None and recPipe.poll():
            MESSAGE = recPipe.recv()

        if MESSAGE is not None:
            #todo wrap with handle
            try:
                s.send(MESSAGE.encode())
                MESSAGE = None
                messageSendAttempts = 0
            except socket.timeout:
                messageSendAttempts += 1
                #todo set maximum send attempts, signal curses to exit and notify user if exceeded

        #rec timeout ignored
        data = s.recv(BUFFER_SIZE)
        if data:
            data = data.decode()
            sendPipe.send(data)

            #note this function uses the stderr stream but that will mess with curses
            #  unless you run the program with 2>logfile.txt
            #  but we can use turn log() into a silent function before turing in for demo
            cursesIO.log("Network recieved data:" + data + "\n")


    #todo send notification of quit to server so it can send poison pill to other client

    #send termination message s.send(MESSAGE.encode())
    print("closing connection")
    #close connection
    s.close()

if __name__ == "__main__":
    main(sys.argv)