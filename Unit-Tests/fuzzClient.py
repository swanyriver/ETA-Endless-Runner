#/usr/bin/python2.7
# references
# https://wiki.python.org/moin/TcpCommunication 
import sys
import socket
import random
import time


##-- Functions --##

#user is either vertical or horizontal  
def getUserInput(user):
    userInput = raw_input(user+'>')
    return userInput

##-- MAIN --##
def main(argv):
    #specify host name and port number on the command line.
    TCP_IP = argv[1]
    TCP_PORT = int(argv[2])
    BUFFER_SIZE = 1024

    NumClients = 1 if len(argv) < 4 else int(argv[3])

    #measure in seconds
    INTERVAL = 1
    #0-1 Larger percent means connected sockets send messages more often
    #    larger percent means more likeley that multiple messages will be sent from different clients at near same time
    BIAS = .7

    #--connect to server--#
    #create sock stream and connect
    sockets = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for _ in range(NumClients)]

    for s in sockets:
        s.connect((TCP_IP, TCP_PORT))
        s.settimeout(.2)

    actions = list("wasd" * 5) + ["/hey there other player", "/yeah go that way", "/good job", "/oh watchout"]

    lastSend = 0

    while True:
        for i,s in enumerate(sockets):
            try:
                updateFromServer = s.recv(BUFFER_SIZE)
                updateFromServer = updateFromServer.strip()
                if updateFromServer:
                    print "<client %d> recieved: " % i, updateFromServer
            except socket.timeout:
                pass

            if time.time() - lastSend > INTERVAL:
                lastSend = time.time()
                if random.random() > BIAS: continue
                msg = random.choice(actions)
                print "<client %d> sent:%s"%(i,msg)
                s.sendall(msg + "\n")






    ############################################################
    #### curses process has ended ##############################
    ############################################################

    #send termination message s.send(MESSAGE.encode())
    print "(NET): closing connection"
    #close connection
    for s in sockets:
        s.close()

#--MAIN--#
if __name__ == "__main__":
    main(sys.argv)
