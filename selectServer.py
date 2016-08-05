import socket
import threading
import thread
import SocketServer
import sys
import select
import game_state
import gameFunctions
import networkKeys

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        serverActive=True
        # self.request is the TCP socket connected to the client
        cur_thread = threading.current_thread()
        myMessageQue = []

        #send first game room/map to client and add queue to directory
        if select.select([self.request],[],[]) != ([],[],[]):
            # if not all actions have been taken assign one set to this thread
            if availableActionSets:
                allowedActionsForThreads[cur_thread.ident] = availableActionSets.pop()
            self.request.sendall(game.get_update()+ "\n")
            threadOutgoingMessages[cur_thread.ident] = myMessageQue
        else:
            print "resource not available to read"

        while serverActive:

            if myMessageQue:
                if select.select([],[self.request],[]) != ([],[],[]):
                    # copy refrence to strings to be sent and empty que in dictionary
                    messagesToSend = list(myMessageQue)
                    del myMessageQue[:]
                else:
                    print "resource not available for write"
                for msg in messagesToSend:
                    self.request.sendall(msg + "\n")


            received=""
            try:
                received=self.request.recv(1024)
                received = received.strip()
                #note:recv'd doesn't have to be 1024
            except:
                pass

            if received==0:
                serverActive=False

            elif received !="":
                #use repr to show whitespace explicitly
                response = "{}: {}".format(cur_thread.name, repr(received))
                #print client response
                print response

                if received[0] == networkKeys.ACTIONS.chat:
                    ## relay chat message
                    if received[0] == networkKeys.ACTIONS.chat:
                        print "(NETWORK) chat received: ", repr(received)
                    for threadIdent, theirmessageQue in threadOutgoingMessages.items():
                        if threadIdent != cur_thread.ident: theirmessageQue.append(received)
                    print "(NETWORK) chat received: ", repr()

                elif cur_thread.ident in allowedActionsForThreads and \
                                received in allowedActionsForThreads[cur_thread.ident]:
                    if select.select([],[self.request],[]) != ([],[],[]):

                        updatedState = game.get_change_request(received)
                        for threadIdent, theirmessageQue in threadOutgoingMessages.items():
                            if threadIdent != cur_thread.ident: theirmessageQue.append(updatedState)
        

                    ## send client movement
                    print "sent to client: " + updatedState
                    self.request.sendall(updatedState + "\n")

                else:
                    continue



class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    # Port 0 selects an arbitrary unused port
    HOST, PORT = "localhost", 9999
    ##create lock object
    lock = threading.Lock()
    #global variables/objects must be created in main prior to threading
    global count

     #-- client code --#
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    #print port so client can connect
    print port

    #create a new game state
    game = game_state.Gamestate()

    allowedActionsForThreads = {}

    availableActionSets = [
        [networkKeys.ACTIONS.left, networkKeys.ACTIONS.right],
        [networkKeys.ACTIONS.up, networkKeys.ACTIONS.down],
    ]

    threadOutgoingMessages = {}

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server loop running in thread:", server_thread.name

    while True:
        continue

    server.shutdown()
    server.server_close()


