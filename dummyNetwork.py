import cursesIO
from multiprocessing import Process, Pipe
from log import log
import dummyGameServer

cursesEnd, networkEnd = Pipe(duplex=True)
cursesProcess = Process(target=cursesIO.cursesEngine, args=(cursesEnd,))
cursesProcess.start()

gameServer = dummyGameServer.DummyGameServer()

#first game state
gameUpdate = gameServer.getGameUpdate()
log("(DUMMY NET MSG-TO-CURSES):" + gameUpdate + "\n")
networkEnd.send(gameUpdate)

#this dummy network will only be able to provide the curses with an update after action
while cursesProcess.is_alive():

    if networkEnd.poll():
        msg = networkEnd.recv()
        log("(DUMMY NET MSG-FROM-CURSES):" + str(type(msg)) + str(msg) + "\n")

        if msg == "w":
            gameServer.moveUp()
        elif msg == "a":
            gameServer.moveLeft()
        elif msg == "s":
            gameServer.moveDown()
        elif msg == "d":
            gameServer.moveRight()

        if msg in "wasd":
            gameUpdate = gameServer.getGameUpdate()
            log("(DUMMY NET MSG-TO-CURSES):" + gameUpdate + "\n")
            networkEnd.send(gameUpdate)

