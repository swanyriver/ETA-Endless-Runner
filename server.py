#!/usr/bin/python2.7
import SocketServer
#Server
#references : https://docs.python.org/2/library/socketserver.html

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The request handler class for our server.
    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        serverActive=True
        # self.request is the TCP socket connected to the client
        while serverActive:
            received=self.request.recv(1024)
            if received==0:
                serverActive=False
            else:
                self.data = received.strip()
                print "{} wrote:".format(self.client_address[0])
                print self.data
                # just send back the same data, but upper-cased
                self.request.sendall(self.data.upper()+"\n")
                #TODO call function to process user movement
                #TODO call function to pass user text back to other client


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999 #TODO remove magic # 9999

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()


