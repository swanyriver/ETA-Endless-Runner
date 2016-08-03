#!/usr/bin/python2.7
import SocketServer
import game_state

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

        game = game_state.Gamestate()
        self.request.sendall(game.get_update()+ "\n")

        while serverActive:
            received=self.request.recv(1024)
            if received==0:
                serverActive=False
            else:
                data = received.strip()
                print "recieved from " + str(self.client_address[0]) + ": " + data

                #todo intercept and forward chat message instead of send to game

                #request to move player
                updatedState = game.get_change_request(data)
                print "sent to client: " + updatedState
                self.request.sendall(updatedState + "\n")


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999 #TODO remove magic # 9999

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()


