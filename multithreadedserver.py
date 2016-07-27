import threading
import SocketServer
import networkKeys
import game_state

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        serverActive=True
        # self.request is the TCP socket connected to the client
        self.request.setblocking(0)

        while serverActive:
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
                cur_thread = threading.current_thread()
                #use repr to show whitespace explicitly
                response = "{}: {}".format(cur_thread.name, repr(received))
                #print client response
                print response

                # todo (Megan) Was this for Testing?
                #send response
                #self.request.sendall(response)

                # if received in networkKeys.MOVEMENTS:
                #     lock.acquire()
                #
                #     #check if client is vertical or horizontal
                #     if cur_thread.name=="Thread-2":
                #         #TODO allow horizontal movement
                #         updatedState = game.get_change_request(data)
                #         pass
                #
                #     elif cur_thread.name=="Thread-3":
                #         #TODO allow vertical movement
                #         updatedState = game.get_change_request(data)
                #         pass
                #
                #     else:
                #         print "Too many players, please wait"
                #
                #     lock.release()

                if received[0] == networkKeys.ACTIONS.chat:
                    # todo relay chat message
                    print "(NETWORK) chat received: ", repr()

                elif received in allowedMovements[cur_thread.name]:
                    lock.acquire()
                    updatedState = game.get_change_request(received)
                    lock.release()

                #-- End of locked thread --#

                    #todo send to other client
                    print "sent to client: " + updatedState
                    self.request.sendall(updatedState + "\n")

                else:
                    continue
                ## send client movement    



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

    #create a new game state
    game = game_state.Gamestate()

    allowedMovements = {
        "Thread-2": [networkKeys.ACTIONS.left, networkKeys.ACTIONS.right],
        "Thread-3": [networkKeys.ACTIONS.up, networkKeys.ACTIONS.down],
    }

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
