import socket
import threading
import thread
import SocketServer
import time

#TODO object definition
count=0

def test(count):
    #lock.acquire()
    try:
        count += 1
        print count 
        time.sleep(25)
   
    finally:
       print "done"# lock.release()
       return count

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        serverActive=True
        # self.request is the TCP socket connected to the client
        self.request.setblocking(0)
        
        global count

        while serverActive:
            received=""
            try:
                received=self.request.recv(1024) #don't think recv works here
            except:
                pass
            
            if received==0:#TODO fix close reason
                serverActive=False
            elif received !="":
                cur_thread = threading.current_thread()
                response = "{}: {}".format(cur_thread.name, received)
                print response
                self.request.sendall(response)
                #TODO 
                print "current count:"
                print count

                if received=="LOCK":
                    lock.acquire()
                    print "aquired lock"
                    #Do stuff here
                    count=test(count)
                    print "Test complete"
                    lock.release()
                    print "released lock"
                else:
                    continue
                #TODO NOT REACHING THIS LINE
                print "send info to client now, current count:"
                print count

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 9998
    ##TODO
    lock = threading.Lock()

    #-- client code --# 
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address
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
        #if clientMsg=="\quit"
        #   live=False
        #printclient msg
        continue

    server.shutdown()
    server.server_close()
