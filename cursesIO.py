# Proof of concept test for curses based input and output on flip server

import curses
import time
from multiprocessing import Process, Pipe
import testingServer
from log import log

# Macros for curses magic number functions
ON = 1
OFF = 0

SCREEN_REFRESH = .25 # 4-FPS
SCREEN_REFRESH = .05

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

# #todo will also need to send player identifier
# def outgoingJson (action):
#     outjson = json.dumps({"action": action, "clientID": "todo define method for distinguishing clients"})
#     log(outjson)
#     return outjson

class localGame():
    def __init__(self, charDrawing, charStarty, charStartx):
        self.charDrawing = charDrawing
        self.charX = charStartx
        self.charY = charStarty

def respondToInput(in_char_num, sendpipe):
    action = control_scheme.get(in_char_num)
    if action:
        log("sending input to server: " + str(action) + "\n")
        sendpipe.send(action)


def refreshScreen(screen, gameState):
    #log("Refreshing screen\n")
    screen.erase()
    # for entity in gameState:
    #     y,x = entity.y, entity.x
    #     for line in entity.drawable.drawing:
    #          #todo use proper color pair
    #          screen.addstr(y, x, line, curses.color_pair(1))
    #          y += 1

    y, x = gameState.charY, gameState.charX
    for line in gameState.charDrawing:
        # todo use proper color pair
        screen.addstr(y, x, line, curses.color_pair(0))
        y += 1


def checkForUpdate(recPipe, localGame):
    while recPipe.poll():
        localGame.charY, localGame.charX = recPipe.recv()



# input is captured constantly but screen refreshes on interval
# no-sleep version of process loop
def constantInputReadLoop(screen, localGame, sendPipe, recPipe):
    log("constant input loop initiated\n")

    lastRefresh = 0

    while True:
        checkForUpdate(recPipe, localGame)
        if time.time() - lastRefresh > SCREEN_REFRESH:
            lastRefresh = time.time()
            refreshScreen(myScreen, localGame)

        # primary input and output loop
        char_in = screen.getch()

        if char_in != curses.ERR:
            # log("input: %r %s %r\n" %
            #                  (char_in, chr(char_in) if 0 <= char_in < 256 else "{Non Ascii}",
            #                   curses.keyname(char_in)))
            respondToInput(char_in, sendPipe)

            if control_scheme.get(char_in) == ACTIONS.quit:
                break



#temp
charDraw = ["  *  ",
                " <*> ",
                "<***>",
                " ^ ^ "]


def cursesEngine(sendPipe, recPipe):
    myScreen = startCurses()

    #todo determine if terminal is sufficient size for predifined 80 X 24 minus chat window
    maxY, maxX = myScreen.getmaxyx()

    #todo get first renderable world from server

    #get characters initial position before begining render
    recPipe.poll(None)
    y, x = recPipe.recv()

    gamestate = localGame(charDraw, y, x)

    constantInputReadLoop(myScreen, gamestate, sendPipe, recPipe)

    exitCurses(myScreen)


#used for independent testing
if __name__ == '__main__':

    sendPipe, gamein = Pipe()
    recPipe, gameout = Pipe()

    myScreen = startCurses()

    maxY, maxX = myScreen.getmaxyx()

    gameServer = Process(target=testingServer.gameServer, args=(maxY, maxX, gamein, gameout))
    gameServer.start()
    
    recPipe.poll(None)
    y,x = recPipe.recv()

    gamestate = localGame(charDraw, y, x)

    constantInputReadLoop(myScreen, gamestate, sendPipe, recPipe)

    exitCurses(myScreen)
