import socket
import threading
import SocketServer

#TODO TODO
class dummyGameState(threading.Lock):
    print "lock"

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        serverActive=True
        # self.request is the TCP socket connected to the client
        self.request.setblocking(0)
        #TODO TODO
        GS=dummyGameState.lock()

        while serverActive:
            received=""
            try:
                received=self.request.recv(1024) #don't think recv works here
            except:
                pass
            
            if received==0:
                serverActive=False
            elif received !="":
                cur_thread = threading.current_thread()
                response = "{}: {}".format(cur_thread.name, received)
                print response
                #TODO TODO
                if GS.locked():
                    print "thread is locked Please wait"
                elif response=="0":
                    GS.aquire()
                elif response=="1":
                    GS.release()
                self.request.sendall(response)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 9999
    
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
