import socket
import threading
import SocketServer
import sys

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print "Received: {}".format(response)
    finally:
        sock.close()

##-- MAIN --##
def main(argv):
    #specify host name and port number on the command line.
    ip = sys.argv[1] 
    port = int(sys.argv[2])  
    client(ip, port, "Hello World 1")
    #TODO send data in loop
    
#--MAIN--#
if __name__ == "__main__":
    main(sys.argv)
