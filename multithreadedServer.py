#!/usr/bin/python2.7
import socket
import threading
from SocketServer import ThreadingTCPServer
from SocketServer import BaseRequestHandler

class ThreadedTCPRequestHandler(BaseRequestHandler):

    #def handle(self):
    #    data = self.request.recv(1024)
    #    cur_thread = threading.current_thread()
    #    response = "{}: {}".format(cur_thread.name, data)
    #    self.request.sendall(response)

    def handle(self):
        serverActive=True
        # self.request is the TCP socket connected to the client
        while serverActive:
            received=self.request.recv(1024)
            if received==0:
                serverActive=False
            else:
                data = self.request.recv(1024)
                print data
                cur_thread = threading.current_thread()
                response = "{}: {}".format(cur_thread.name, data)
                self.request.sendall(response)
                # just send back the same data, but upper-cased
                self.request.sendall(self.data.upper()+"\n")
                #TODO call function to process user movement
                #TODO call function to pass user text back to other client

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 0

    server = ThreadingTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread()#target=server.serve_forever) <change serve forever to allow clients to terminate
    # Exit the server thread when the main thread terminates
   
    #server_thread.daemon = True ####<<TODO remove
    server_thread.start()
    print "Server loop running in thread:", server_thread.name
    print "server port:",port
    print "server host:",ip
    while 1:
        continue

    #if()<<TODO replace while with this
    server.shutdown()
    server.server_close()
    print "server is now closed"
