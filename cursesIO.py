import curses
import time
from log import log
import graphicAssets
import gameEntities
import json
from networkKeys import *
from collections import namedtuple
from itertools import izip_longest

# Macros for curses magic number functions
ON = 1
OFF = 0

SCREEN_REFRESH = .05 # 20FPS
TICK = .5            # starting frequency of frame transitions for animation,  half second
GAMEWINDOW_ROWS = 20
GAMEWINDOW_COLS = 80

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

cursesColors = [(curses.COLOR_BLACK, graphicAssets.GraphicAsset.kBlack),
                (curses.COLOR_RED, graphicAssets.GraphicAsset.kRed),
                (curses.COLOR_GREEN, graphicAssets.GraphicAsset.kGreen),
                (curses.COLOR_YELLOW, graphicAssets.GraphicAsset.kYellow),
                (curses.COLOR_BLUE, graphicAssets.GraphicAsset.kBlue),
                (curses.COLOR_MAGENTA, graphicAssets.GraphicAsset.kMagenta),
                (curses.COLOR_CYAN, graphicAssets.GraphicAsset.kCyan),
                (curses.COLOR_WHITE, graphicAssets.GraphicAsset.kWhite)]


#simple wrapper around int to keep all animations on same speed
class TimingClock():
    def __init__(self):
        self.tick = TICK
        self.time = time.time()

    def getTime(self):
        return self.time

    def setFrameTime(self):
        self.time = time.time()

    def speedUo(self):
        self.tick /= 2
        log("(CURSE ANIM): increasing speed of animations %f seconds-a-frame\n" % self.tick)

    def slowDown(self):
        self.tick *= 2
        log("(CURSE ANIM): increasing speed of animations %f seconds-a-frame\n" % self.tick)


# gamEntity subclass for encapsulating the drawing related methods
class DrawableEntity(gameEntities.gameEntity):
    Pixel = namedtuple("pixel", ['y', 'x', 'char', 'color'])

    def __init__(self, graphicAsset, y, x, timingClock, colorDictionary):
        super(DrawableEntity, self).__init__(graphicAsset, y, x)

        if not len(graphicAsset.drawings) > 1:
            self.getDrawing = self.getDrawingNoAnim
        else:
            self.currentFrame = 0
            self.lastFrameTime = time.time()

        self.timingClock = timingClock
        self.colorDict = colorDictionary
        self.drawingCache = None

        self.frameDurations = [1] * len(self.graphic.drawings)
        self.totalDuration = sum(self.frameDurations) * self.timingClock.tick


    def getColorInt(self, frame, y, x):
        try:
            return curses.color_pair(self.colorDict.get(
                (self.graphic.colorFrames[frame][y][x]
                 if self.graphic.colorFrames else graphicAssets.GraphicAsset.kWhite,
                 self.graphic.backgroundFrames[frame][y][x]
                 if self.graphic.backgroundFrames else graphicAssets.GraphicAsset.kBlack), 0))
        except (IndexError, TypeError):
            log("(CURSES RENDER ERROR) Error accessing color arrays")
            # return white on black
            return curses.color_pair(0)


    def getDrawingFrame(self, frame):

        if self.drawingCache and (self.y, self.x, frame) == self.drawingCache[0]:
            return self.drawingCache[1]

        pixelArray = [DrawableEntity.Pixel(y + self.y, x + self.x,
                                           ord(self.graphic.drawings[frame][y][x]),
                                           self.getColorInt(frame, y, x))
                      for y in range(self.graphic.height)
                      for x in range(self.graphic.width)
                      if (y, x) in self.graphic.hitbox]
        self.drawingCache = ((self.y, self.x, frame), pixelArray)
        return pixelArray


    def getDrawingNoAnim(self):
        return self.getDrawingFrame(0)

    def getDrawing(self):

        timeSinceFrameChange = (self.timingClock.getTime() - self.lastFrameTime)

        # advance current frame to appropriate frame
        #  if TICK < SCREEN_REFRESH (currently 1/10) or program has hung frames might be skipped (intended effect)
        while timeSinceFrameChange >= self.frameDurations[self.currentFrame] * self.timingClock.tick:
            timeSinceFrameChange -= self.frameDurations[self.currentFrame] * self.timingClock.tick
            self.currentFrame = (self.currentFrame + 1) % len(self.graphic.drawings)
            self.lastFrameTime = self.timingClock.getTime()

        return self.getDrawingFrame(self.currentFrame)


class renderPlayer(DrawableEntity):
    def __init__(self, timingClock, colorDictionary):
        super(renderPlayer, self).__init__(graphicAssets.getPlayerAsset(), None, None, timingClock, colorDictionary)
        #todo create 2 or 4 way symmetrical drawings for character
        #todo create rotated or flipped drawings of character arrays to load before drawing
        #self.letfFaceDrawing =

    # def getDrawing(self):
    #     return super(renderPlayer, self).getDrawing()

    def setYX(self, y, x):
        #todo check new y and x and swap drawing for proper rotation
        super(renderPlayer, self).setYX(y, x)



class gameState():
    def __init__(self, assets, maxY, maxX, colorDict):
        self.maxX = maxX
        self.maxY = maxY
        self.entities = []
        self.assets = assets
        self.timingClock = TimingClock()
        self.colorDict = colorDict
        self.player = renderPlayer(self.timingClock, colorDict)

    def newScreen(self, newEntities):
        self.entities = []
        for e in newEntities:
            self.entities.append(DrawableEntity(
                y=e['y'],
                x=e['x'],
                graphicAsset=self.assets[e['graphicAsset']],
                timingClock=self.timingClock,
                colorDictionary=self.colorDict
            ))
        #character position is invalidated on new screen
        self.player.setYX(None, None)
        log("(CURSES-GAME): new screens entities: (%d) "%len(self.entities)
            + str(self.entities) + "\n")

    def updateCharPos(self, y, x):
        self.player.setYX(y, x)
        log("(CURSES-GAME): char new pos %s\n" % (str(self.player.getYX())))

    def drawEntity(self, entity, screen):
        for pixel in filter(lambda p: 0 <= p.y < self.maxY and 0 <= p.x < self.maxX,
                            entity.getDrawing()):
            try:
                screen.addch(*pixel)
            except curses.error:
                # curses raises a superfulous error when drawing on the bottom right char of a subdivided window
                pass

    def render(self, screen):
        screen.erase()
        self.timingClock.setFrameTime()
        for e in self.entities:
            self.drawEntity(e, screen)

        if None not in self.player.getYX():
            self.drawEntity(self.player, screen)

        screen.refresh()


def initColors():
    curses.start_color()
    colorDict = {(None,None):0}
    n = 1
    for fgndColor, fgrndKey in cursesColors:
        for bkgrndColor, bkgrndKey in cursesColors:
            curses.init_pair(n, fgndColor, bkgrndColor)
            colorDict[(fgndColor, bkgrndColor)] = n
            colorDict[(fgrndKey, bkgrndKey)] = n
            n += 1

    return colorDict


def startCurses():
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    screen.keypad(ON)
    screen.nodelay(ON)
    curses.curs_set(OFF)
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


def checkForUpdate(recPipe, localGame, chatMan):

    while recPipe.poll():
        networkMessage = recPipe.recv()
        if not networkMessage:
            continue

        #intercept chat messages
        if networkMessage[0] == ACTIONS.chat:
            networkMessage = networkMessage.replace("\n", "")
            log("(CURSES NET-IN CHAT): " + str(networkMessage)[1:] + "\n")
            chatMan.newChatMessage(networkMessage[1:])
            return False, None

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
            return True, networkMessage[kGAMEOVER]

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

    return False, None

# input is captured constantly but screen refreshes on interval
# no-sleep version of process loop
def constantInputReadLoop(gameWindow, networkPipe, localGame, chatMan):
    log("constant input loop initiated\n")

    lastRefresh = 0
    isTypingChatMessage = False

    while True:
        ### primary input and output loop ###

        # check for message from network
        gameOver, message = checkForUpdate(networkPipe, localGame, chatMan)
        if gameOver:
            log("(CURSES GAMEOVER):%r\n"%message)
            break

        # redraw game state acording to frame rate
        if time.time() - lastRefresh > SCREEN_REFRESH:
            lastRefresh = time.time()
            localGame.render(gameWindow)

        # gather input from keyboard and transmit to network if appropriate
        char_in = gameWindow.getch()
        if char_in != curses.ERR:
            # log("input: %r %s %r\n" %
            #                  (char_in, chr(char_in) if 0 <= char_in < 256 else "{Non Ascii}",
            #                   curses.keyname(char_in)))

            # todo switch to chat input method if / char is pressed

            if isTypingChatMessage:
                isTypingChatMessage, msg = chatMan.newChatCharInput(char_in)
                if not isTypingChatMessage and msg and msg:
                    networkPipe.send(msg)

            else:
                if char_in == ord(ACTIONS.chat):
                    isTypingChatMessage = True
                    chatMan.newChatCharInput(char_in)
                else:
                    respondToInput(char_in, networkPipe)

                    if control_scheme.get(char_in) == ACTIONS.quit:
                        log("(CURSES GAMEOVER):%s\n" % "this client pressed quit")
                        break


class ChatManager():
    def __init__(self, chatDisplayWindow, chatEntryLine, colorDict):
        self.chatEntryLine = chatEntryLine
        self.chatDisplayWindow = chatDisplayWindow
        self.COLOR = curses.color_pair(colorDict[(curses.COLOR_WHITE, curses.COLOR_MAGENTA)])
        self.chatDisplayLines, self.width = chatDisplayWindow.getmaxyx()
        self.chatMessages = []
        self.updateChatDisplay()
        self.chatCompose = []
        self.ESCAPE_KEY = 27
        self.RETURN_KEY = 10
        self.PRINTABLE_MIN = 32
        self.PRINTABLE_MAX = 127

    def updateChatDisplay(self):
        self.chatDisplayWindow.erase()
        for y, msg in izip_longest(range(self.chatDisplayLines), self.chatMessages[-self.chatDisplayLines:], fillvalue=""):
            try:
                self.chatDisplayWindow.addstr(y, 0, msg + " " * (self.width - len(msg)), self.COLOR)
            except curses.error:
                pass
        self.chatDisplayWindow.refresh()

    def newChatMessage(self, msg):
        #todo provide way to view old messages, or trim array
        self.chatMessages.append(msg)
        self.updateChatDisplay()


    def _displayChatCursor(self):
        try:
            #erase old char after backspace
            self.chatEntryLine.addch(0, len(self.chatCompose)+1, " ")
        except curses.error:
            pass
        try:
            self.chatEntryLine.addch(0, len(self.chatCompose), "_", curses.A_BLINK | curses.A_REVERSE)
        except curses.error:
            pass

    # retunrs (chat still in progress T/F, msg)
    def newChatCharInput(self, char_in_num):

        log("(CHAT IN) %d\n"%char_in_num)

        if char_in_num == self.ESCAPE_KEY:
            self.chatCompose = []
            self.chatEntryLine.erase()
            self.chatEntryLine.refresh()
            return False, None

        if char_in_num == curses.KEY_ENTER or char_in_num == self.RETURN_KEY:
            self.chatCompose.append("\n")
            msg = "".join(self.chatCompose)
            self.chatCompose = []
            self.chatEntryLine.erase()
            self.chatEntryLine.refresh()
            return False, (msg if len(msg) > 2 else None)

        if char_in_num == curses.KEY_BACKSPACE:
            self.chatCompose.pop()
            if len(self.chatCompose):
                self._displayChatCursor()
            else:
                self.chatEntryLine.erase()
            self.chatEntryLine.refresh()
            #exit chat if all characters deleted
            return len(self.chatCompose) > 0, None

        if self.PRINTABLE_MIN <= char_in_num <= self.PRINTABLE_MAX and len(self.chatCompose) < self.width-1:
            self.chatCompose.append(chr(char_in_num))
            try:
                self.chatEntryLine.addch(0, len(self.chatCompose)-1, chr(char_in_num))
                self._displayChatCursor()
            except curses.error:
                pass
            self.chatEntryLine.refresh()

        return True, None



def cursesEngine(networkPipe):
    gameWindow = startCurses()
    colorDict = initColors()

    gameWindow.resize(GAMEWINDOW_ROWS, GAMEWINDOW_COLS)
    chatDisplayWindow = curses.newwin(3, 80, 20, 0)
    chatEntryLine = curses.newwin(1, 79, 23, 0)
    chatMan = ChatManager(chatDisplayWindow, chatEntryLine, colorDict)

    localGame = gameState(graphicAssets.getAllAssets(), GAMEWINDOW_ROWS, GAMEWINDOW_COLS, colorDict)

    constantInputReadLoop(gameWindow, networkPipe, localGame, chatMan)

    exitCurses(gameWindow)
    log("(CURSES): curses screen exited\n")

