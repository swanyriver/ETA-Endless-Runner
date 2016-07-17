# Proof of concept test for curses based input and output on flip server

import curses
import time
from multiprocessing import Process, Pipe
from log import log
import graphicAssets
import gameEntities
import json
from networkKeys import *

# Macros for curses magic number functions
ON = 1
OFF = 0

SCREEN_REFRESH = .05 # 20FPS

# sadly there is no Enum class or pattern in python 2.x so this class will need to be used with extreme caution
class ACTIONS():
    up = "w"
    down = "s"
    left = "a"
    right = "d"
    quit = "q"

# int to int, mapping keyboard key to action enum
control_scheme = {
    curses.KEY_UP:ACTIONS.up,
    ord('w'):ACTIONS.up,
    curses.KEY_DOWN:ACTIONS.down,
    ord('s'):ACTIONS.down,
    curses.KEY_LEFT:ACTIONS.left,
    ord('a'):ACTIONS.left,
    curses.KEY_RIGHT:ACTIONS.right,
    ord('d'):ACTIONS.right,
    27:ACTIONS.quit, #escape key
    ord('q'):ACTIONS.quit
}

class gameState():
    def __init__(self, assets, maxY, maxX):
        self.maxX = maxX
        self.maxY = maxY
        self.entities = []
        self.assets = assets
        #todo this is very fragile, consider another way of selecting character drawing
        self.character = gameEntities.gameEntity(assets["character"], None, None)

    def newScreen(self, newEntities):
        self.entities = []
        for e in newEntities:
            e['graphicAsset'] = self.assets[e['graphicAsset']]
            self.entities.append(gameEntities.gameEntity(**e))
        #character position is invalidated on new screen #todo ensure char pos is always transmitted after new screen
        self.character.setYX(None, None)
        log("(CURSES-GAME): new screens entities: (%d) "%len(self.entities)
            + str(self.entities) + "\n")

    def updateCharPos(self, y, x):
        self.character.setYX(y, x)
        log("(CURSES-GAME): char new pos %s\n"%(str(self.character.getYX())))

    def drawEntity(self, entity, screen):
        for pixel in filter(lambda p: 0 <= p.y < self.maxY and 0 <= p.x < self.maxX,
                            entity.getDrawing()):
            screen.addch(*pixel)

    def render(self, screen):
        screen.erase()
        for e in self.entities:
            self.drawEntity(e, screen)

        if None not in self.character.getYX():
            self.drawEntity(self.character, screen)


def startCurses():
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    screen.keypad(ON)
    screen.nodelay(ON)
    curses.curs_set(OFF)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_YELLOW)
    return screen


def exitCurses(screen):
    curses.nocbreak()
    screen.keypad(OFF)
    screen.nodelay(OFF)
    curses.curs_set(ON)
    curses.echo()
    curses.endwin()


def respondToInput(in_char_num, sendpipe):
    action = control_scheme.get(in_char_num)
    if action:
        log("(CURSES NET-OUT): " + str(action) + "\n")
        sendpipe.send(action)


def checkForUpdate(recPipe, localGame):

    while recPipe.poll():
        networkMessage = recPipe.recv()
        if not networkMessage:
            continue
        log("(CURSES NET-IN): " + str(networkMessage) + "\n")
        try:
            networkMessage = json.loads(networkMessage)
        except ValueError:
            log("(CURSES NET-IN ERROR): json parsing error\n")
            continue
        if not networkMessage or not isinstance(networkMessage, dict):
            log("(CURSES NET-IN ERROR): network message is not a k:v dict\n")
            continue

        #process parsed network message
        #end parsing immediately on game over message
        if kGAMEOVER in networkMessage:
            return False, networkMessage[kGAMEOVER]

        if kSCREEN in networkMessage:
            entitiesArray = networkMessage[kSCREEN]
            if not isinstance(entitiesArray, list):
                log("(CURSES NET-IN ERROR): screen value is not an array\n")
            else:
                entitiesArray = filter(lambda e: (isinstance(e, dict) and
                                 len(e) == len(ENTITYKEYS) and
                                 all(isinstance(e.get(k, None), typ) for k, typ in ENTITYKEYS.items())),
                                 entitiesArray)
                if not entitiesArray:
                    log("(CURSES NET-IN ERROR): screen array contains no valid entities\n")
                else:
                    localGame.newScreen(entitiesArray)

        if kCHAR in networkMessage:
            posDict = networkMessage[kCHAR]
            #assert that charpos is dict and has necesary fields with correct types
            if isinstance(posDict, dict) and all(isinstance(posDict.get(k,None),int) for k in ("y","x")):
                localGame.updateCharPos(y=posDict['y'], x=posDict['x'])
            else:
                log("(CURSES NET-IN ERROR): player position dict badly formed")

    return True, None

# input is captured constantly but screen refreshes on interval
# no-sleep version of process loop
def constantInputReadLoop(screen, networkPipe, localGame):
    log("constant input loop initiated\n")

    lastRefresh = 0

    while True:
        ### primary input and output loop ###

        # check for message from network
        gameOver, message = checkForUpdate(networkPipe, localGame)
        if not gameOver:
            log("(CURSES GAMEOVER):%r\n"%message)
            break

        # redraw game state acording to frame rate
        if time.time() - lastRefresh > SCREEN_REFRESH:
            lastRefresh = time.time()
            localGame.render(screen)

        # gather input from keyboard and transmit to network if appropriate
        char_in = screen.getch()
        if char_in != curses.ERR:
            # log("input: %r %s %r\n" %
            #                  (char_in, chr(char_in) if 0 <= char_in < 256 else "{Non Ascii}",
            #                   curses.keyname(char_in)))

            # todo switch to chat input method if / char is pressed

            respondToInput(char_in, networkPipe)

            if control_scheme.get(char_in) == ACTIONS.quit:
                log("(CURSES GAMEOVER):%s\n" % "this client pressed quit")
                break


def cursesEngine(networkPipe):
    myScreen = startCurses()

    #todo determine if terminal is sufficient size for predifined 80 X 24 minus chat window
    maxY, maxX = myScreen.getmaxyx()

    #-1 because cant draw on bottom right pixel
    #todo reserve space for chat
    localGame = gameState(graphicAssets.getAllAssets(), maxY-1, maxX)

    constantInputReadLoop(myScreen, networkPipe, localGame)

    exitCurses(myScreen)
    log("(CURSES): curses screen exited\n")
