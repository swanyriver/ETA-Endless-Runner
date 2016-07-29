import socket
import threading
import thread
import SocketServer
import sys
import select

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
                #TODO ######################################
                if select.select([self.request],[],[]) != ([],[],[]):
                    received=self.request.recv(1024) 
            
                    if received !="":
                        cur_thread = threading.current_thread()
                        response = "{}: {}".format(cur_thread.name, received)
                        print response
                        self.request.sendall(response)
                else:
                    print select.select([self.request],[],[])
                    print "wtf"
                #TODO#####################################
       
            except OSError as err:
                print("OS error: {0}".format(err))
            except ValueError:
                print("Could not convert data to an integer.")
            except:
                print("Unexpected error:", sys.exc_info())
                serverActive=False #TODO BREAK HERE
                pass
            

                continue
                ## TODO send client movement    
                ## print "sent to client: " + updatedState
                #self.request.sendall(updatedState + "\n")
                    

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    # Port 0 selects an arbitrary unused port
    HOST, PORT = "localhost", 9998
    ##create lock object
    lock = threading.Lock()

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

    # TODO use to replace while : server_thread.join()


    server.shutdown()
    server.server_close()
