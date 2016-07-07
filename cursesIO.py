# Proof of concept test for curses based input and output on flip server

import curses
import sys
import time
import json
import drawable

# Macros for curses magic number functions
ON = 1
OFF = 0

SCREEN_REFRESH = .25 # 4-FPS
SCREEN_REFRESH = .05

# sadly there is no Enum class or pattern in python 2.x so this class will need to be used with extreme caution
class ACTIONS():
    up = "up"
    down = "down"
    left = "left"
    right = "right"
    quit = "quit"

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

class gameEntity():
    def __init__(self, drawable, y, x):
        self.drawable = drawable
        self.y = y
        self.x = x

        #todo init animation
        #self.drawingIndex = 0
        #self.timeToChange =

def log(str):
    sys.stderr.write(str)


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
    curses.nocbreak();
    screen.keypad(OFF);
    screen.nodelay(OFF)
    curses.curs_set(ON)
    curses.echo()
    curses.endwin()

#todo will also need to send player identifier
def outgoingJson (action):
    outjson = json.dumps({"action": action, "clientID": "todo define method for distinguishing clients"})
    log(outjson)
    return outjson

#todo, change param to outpipe,  dont modify object
def respondToInput(in_char_num, gameState):
    action = control_scheme.get(in_char_num)
    directional_change = {
        ACTIONS.left: (0, -1),
        ACTIONS.right: (0, 1),
        ACTIONS.up: (-1, 0),
        ACTIONS.down: (1, 0)
    }
    if action:
        positionDelta = directional_change.get(action, (0, 0))
        log("Respond to input" + str(positionDelta) + "\n")

        gameState[0].y += positionDelta[0]
        gameState[0].x += positionDelta[1]
        #log("character at: %s\n"%(str(gameState.getCharPos())))


def refreshScreen(screen, gameState):
    #log("Refreshing screen\n")
    screen.erase()
    for entity in gameState:
        y,x = entity.y, entity.x
        for line in entity.drawable.drawing:
             #todo use proper color pair
             screen.addstr(y, x, line, curses.color_pair(1))
             y += 1


def checkForUpdate(inpipe, localGame):
    pass


# input is captured constantly but screen refreshes on interval
# no-sleep version of process loop
def constantInputReadLoop(screen, localGame, outpipe, inpipe):
    log("constant input loop initiated\n")
    lastRefresh = time.time()
    while True:
        # primary input and output loop
        char_in = screen.getch()
        if control_scheme.get(char_in) == ACTIONS.quit:
            break
        if char_in != curses.ERR:
            log("input: %r %s %r\n" %
                             (char_in, chr(char_in) if 0 <= char_in < 256 else "{Non Ascii}",
                              curses.keyname(char_in)))

        respondToInput(char_in, localGame)
#        respondToInput(char_in, outpipe)

        checkForUpdate(inpipe, localGame)
        if time.time() - lastRefresh > SCREEN_REFRESH:
            lastRefresh = time.time()
            refreshScreen(myScreen, localGame)


#temp
charDraw = ["  *  ",
                " <*> ",
                "<***>",
                " ^ ^ "]
character = gameEntity(drawable.drawable(charDraw, "character"),  0, 0 )


if __name__ == '__main__':

    localGame = [character]
    outpipe = None
    inpipe = None


    myScreen = startCurses()

    constantInputReadLoop(myScreen, localGame, outpipe, inpipe)

    exitCurses(myScreen)
