import socket
import threading
import SocketServer

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
#    def handle(self):
#        data = self.request.recv(1024)
#        cur_thread = threading.current_thread()
#        response = "{}: {}".format(cur_thread.name, data)
#        self.request.sendall(response)

    def handle(self):
        serverActive=True
        # self.request is the TCP socket connected to the client
        while serverActive:
            received=self.request.recv(1024) #don't think recv works here
            if received==0:
                serverActive=False
            else:
                cur_thread = threading.current_thread()
                response = "{}: {}".format(cur_thread.name, received)
                self.request.sendall(response)



class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 0
    
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
