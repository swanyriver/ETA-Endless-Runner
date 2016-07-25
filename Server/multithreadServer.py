import socket
import threading
import thread
import SocketServer

#TODO remove TESTING only
def test():
    try:
        count += 1
        print count    
    finally:
       print "done"

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        serverActive=True
        # self.request is the TCP socket connected to the client
        self.request.setblocking(0)
        #client #
        client=0

        while serverActive:
            received=""
            try:
                received=self.request.recv(1024) 
                #note:recv'd doesn't have to be 1024
            except:
                pass
            
            if received==0:
                serverActive=False
                #TODO set condition to gracefully close server
            elif received !="":
                cur_thread = threading.current_thread()
                response = "{}: {}".format(cur_thread.name, received)
                #print client response
                print response
                self.request.sendall(response)

                #check if client is vertical or horizontal
                if cur_thread.name=="Thread-2":
                    client=1
                    #TODO allow horizontal movement
                elif cur_thread.name=="Thread-3":
                    client=2
                    #TODO allow vertical movement
                else:
                    print "Too many players, please wait"

                #TESTING -- replace with item lock
                if received=="LOCK":
                    lock.acquire()
                    print "aquired lock"
                    #Do stuff here
                    test()
                    print "Test complete"
                    lock.release()
                    print "released lock"
                #---#
                else:
                    continue
                print "send info to client now"
                #TODO send game state

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    # Port 0 selects an arbitrary unused port
    HOST, PORT = "localhost", 9998
    ##create lock object
    lock = threading.Lock()
    #global variables/objects must be created in main prior to threading
    global count    

     #-- client code --# 
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    #print port so client can connect
    print port

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server loop running in thread:", server_thread.name

    live=True;
    while live:
    #TODO set server graceful close methods
    #    if clientMsg=="quit":
    #        live=False
    #        print clientMsg
        continue

    server.shutdown()
    server.server_close()
