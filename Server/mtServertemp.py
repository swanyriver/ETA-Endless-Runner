import socket
import threading
import thread
import SocketServer
###
class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        serverActive=True
        # self.request is the TCP socket connected to the client
        self.request.setblocking(0)

        while serverActive:
            received=""
            try:
                received=self.request.recv(1024) 
                #note:recv'd doesn't have to be 1024
            except:
                pass
            
            if received==0:
                serverActive=False

            elif received !="":
                cur_thread = threading.current_thread()
                response = "{}: {}".format(cur_thread.name, received)
                #print client response
                print response
                #send response
                self.request.sendall(response)

                # if received == up/down/left/right
                if received=="w" or received =="a" or received=="s" or received=="d":
                    lock.acquire()

                    #check if client is vertical or horizontal
                    if cur_thread.name=="Thread-2":
                        #allow horizontal movement
                        if received =="a" or received=="d":
                            updatedState = game.get_change_request(data)
                        else:
                            print "You control horizontal movement only!"

                    elif cur_thread.name=="Thread-3":
                        if received =="w" or received=="s":
                            updatedState = game.get_change_request(data)
                        else:
                            print "You control vertical movement only!"

                    else:
                        print "Too many players, please wait"
                                    
                    lock.release()
                #-- End of locked thread --#

                else:
                    continue

                ## send client movement    
                print "sent to client: " + updatedState
                self.request.sendall(updatedState + "\n")
                ##TODO working on joining threads for graceful close
                ##TODO join isn't working
                if(curthread.join()):
                    serverActive=False
                    print "No active connections, closing server"
                    self.request.finish()
                    

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
        continue

    server.shutdown()
    server.server_close()
