import threading
import SocketServer
import sys

import networkKeys
import game_state

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        serverActive=True
        # self.request is the TCP socket connected to the client
        self.request.setblocking(0)

        cur_thread = threading.current_thread()
        myMessageQue = []

        ###### threadsafe strategy ######
        # All threads share an instance of a message-que (threadIdentity#:["msg",""]), gameState, lock
        # the lock is acquired before making any modifications to the game state or the message que dictionary and arrays
        # any game update received from processing input or chat message is copied into all message ques
        #   other than the one receiving the message
        # each socket is only ever read or written from a single thread
        # one lock for both the message que and game will avoid any deadlock complications

        #Thread and socket initialisation
        lock.acquire()
        # if not all actions have been taken assign one set to this thread
        if availableActionSets:
            allowedActionsForThreads[cur_thread.ident] = availableActionSets.pop()

        # send first message of game state before player takes first move
        self.request.sendall(game.get_update()+ "\n")

        # attach this threads message que to messaging dictionary
        threadOutgoingMessages[cur_thread.ident] = myMessageQue
        lock.release()

        while serverActive:

            if myMessageQue:
                lock.acquire()
                # copy refrence to strings to be sent and empty que in dictionary
                messagesToSend = list(myMessageQue)
                del myMessageQue[:]
                lock.release()

                # send all messages in que after releasing lock
                for msg in messagesToSend:
                    self.request.sendall(msg + "\n")


            received=""
            try:
                received=self.request.recv(5000)
                received = received.strip()
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
                    print "(NETWORK) chat received: ", repr(received)

                    lock.acquire()
                    for threadIdent, theirmessageQue in threadOutgoingMessages.items():
                        if threadIdent != cur_thread.ident: theirmessageQue.append(received)
                    lock.release()

                if received[0] == networkKeys.ACTIONS.name:
                    lock.acquire()
                    game.addUserName(received[1:].strip())
                    lock.release()

                elif cur_thread.ident in allowedActionsForThreads and \
                                received in allowedActionsForThreads[cur_thread.ident]:
                    lock.acquire()
                    updatedState = game.get_change_request(received)
                    for threadIdent, theirmessageQue in threadOutgoingMessages.items():
                        if threadIdent != cur_thread.ident: theirmessageQue.append(updatedState)
                    lock.release()

                #-- End of locked thread --#

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
    print "host:127.0.0.1 local"
    print port

    #create a new game state
    game = game_state.Gamestate()

    allowedActionsForThreads = {}

    availableActionSets = [
        [networkKeys.ACTIONS.left, networkKeys.ACTIONS.right],
        [networkKeys.ACTIONS.up, networkKeys.ACTIONS.down],
    ]

    if "-s" in sys.argv:
        availableActionSets = [
            [networkKeys.ACTIONS.left, networkKeys.ACTIONS.right, networkKeys.ACTIONS.up, networkKeys.ACTIONS.down]
        ]

    threadOutgoingMessages = {}

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server loop running in thread:", server_thread.name

    live=True
    while live:
        continue

    server.shutdown()
    server.server_close()
