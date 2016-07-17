import cursesIO
from multiprocessing import Process, Pipe
from log import log
import dummyGameServer
import time
import random

cursesEnd, networkEnd = Pipe(duplex=True)
cursesProcess = Process(target=cursesIO.cursesEngine, args=(cursesEnd,))
cursesProcess.start()

gameServer = dummyGameServer.DummyGameServer()


def sendUpdateToCuresesFromServer():
    global gameUpdate
    gameUpdate = gameServer.getGameUpdate()
    log("(DUMMY NET MSG-TO-CURSES):" + gameUpdate + "\n")
    networkEnd.send(gameUpdate)


#first game state
sendUpdateToCuresesFromServer()

JITTER_TIME = 2
lastRefresh = 0


def inputToMove(msg):
    if msg == "w":
        gameServer.moveUp()
    elif msg == "a":
        gameServer.moveLeft()
    elif msg == "s":
        gameServer.moveDown()
    elif msg == "d":
        gameServer.moveRight()


while cursesProcess.is_alive():

    if time.time() - lastRefresh > JITTER_TIME:
        lastRefresh = time.time()
        #insert jitter to simulate other client
        inputToMove(random.choice("wasd"))
        sendUpdateToCuresesFromServer()

    if networkEnd.poll():
        msg = networkEnd.recv()
        log("(DUMMY NET MSG-FROM-CURSES):" + str(type(msg)) + str(msg) + "\n")

        inputToMove(msg)

        if msg in "wasd":
            sendUpdateToCuresesFromServer()

