import curses
import time
from log import log
import graphicAssets
import gameEntities
import json
import random
from networkKeys import *
from collections import namedtuple
from chatManager import ChatManager

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


# local representation of game state stored on server, updated to reflect changes upon network messages
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
            if e[ENTITY.kGraphicAsset] in self.assets:
                self.entities.append(DrawableEntity(
                    y=e['y'],
                    x=e['x'],
                    graphicAsset=self.assets[e[ENTITY.kGraphicAsset]],
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

    def deathAnimation(self, screen):
        interval = .75
        minInterval = .2
        factor = .7
        PLAYER_DISSOLVE_INTERVAL = .5
        WAIT_IN_BLACKNESS = 1

        if len(self.entities) == 1:
            enemy = self.entities[0]

            #Blink out enemy
            enemyOnTop = False
            while interval > minInterval:
                screen.erase()
                self.drawEntity(self.player if enemyOnTop else enemy, screen)
                self.drawEntity(enemy if enemyOnTop else self.player, screen)
                screen.refresh()
                time.sleep(interval)
                interval *= factor
                enemyOnTop = not enemyOnTop

        else:
            log("(CURSES-RENDER-DEATH) ERROR screen msg at end of game contained more than one entity\n")
            log("(CURSES-RENDER-DEATH) ERROR screen should only contain enemy that killed player\n")

        #slow disolve player graphic
        playerPixels = filter(lambda p: 0 <= p.y < self.maxY and 0 <= p.x < self.maxX, self.player.getDrawing())
        while playerPixels:
            screen.erase()
            for pixel in playerPixels:
                try: screen.addch(*pixel)
                except curses.error: pass
            screen.refresh()
            time.sleep(PLAYER_DISSOLVE_INTERVAL)
            playerPixels.remove(random.choice(playerPixels))

        #pause on empty screen
        screen.erase()
        screen.refresh()
        time.sleep(WAIT_IN_BLACKNESS)


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


def checkForUpdate(recPipe, localGame, chatMan, messagePieces):

    while recPipe.poll():
        nextPiece = recPipe.recv()
        messagePieces.append(nextPiece)

        if not nextPiece or nextPiece[-1] != "\n":
            continue
        else:
            networkMessage = "".join(filter(None,messagePieces))
            if len(messagePieces) > 1:
                log("(CURSES NET-IN JOINED MESSAGE) length:%d, from %d pieces\n"%(len(networkMessage),
                                                                                  len(messagePieces)))
            del messagePieces[:]
            log("(CURSES NET-IN MSG): %s\n"%str(repr(networkMessage)))

        #intercept chat messages
        if networkMessage[0] == ACTIONS.chat:
            networkMessage = networkMessage.replace("\n", "")
            log("(CURSES NET-IN CHAT): " + str(networkMessage)[1:] + "\n")
            chatMan.newChatMessage(networkMessage[1:])
            return False, None

        try:
            networkMessage = json.loads(networkMessage)
        except ValueError:
            log("(CURSES NET-IN ERROR): json parsing error\n")
            continue
        if not networkMessage or not isinstance(networkMessage, dict):
            log("(CURSES NET-IN ERROR): network message is not a k:v dict\n")
            continue

        #process parsed network message
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

        if kGAMEOVER in networkMessage:
            log("(CURSES NET-IN GAME-OVER): killer: %s  gameoverDict:%s\n" % (
                str(networkMessage.get(kSCREEN, None)), str(networkMessage[kGAMEOVER])))
            return True, networkMessage[kGAMEOVER]

    return False, None

# input is captured constantly but screen refreshes on interval
# no-sleep version of process loop
def constantInputReadLoop(gameWindow, networkPipe, localGame, chatMan):
    log("constant input loop initiated\n")

    lastRefresh = 0
    isTypingChatMessage = False
    messagePieces = []

    while True:
        ### primary input and output loop ###

        # check for message from network
        gameOver, message = checkForUpdate(networkPipe, localGame, chatMan, messagePieces)
        if gameOver:
            chatMan.eraseAll()
            localGame.deathAnimation(gameWindow)
            return message

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

            if isTypingChatMessage:
                isTypingChatMessage, msg = chatMan.newChatCharInput(char_in)
                if not isTypingChatMessage and msg:
                    networkPipe.send(msg)
                    # display users sent message in chat log
                    # todo delineate sent messages with a different color or leading character
                    chatMan.newChatMessage(msg[1:-1])

            else:
                if char_in == ord(ACTIONS.chat):
                    isTypingChatMessage = True
                    chatMan.newChatCharInput(char_in)
                else:
                    respondToInput(char_in, networkPipe)

                    if control_scheme.get(char_in) == ACTIONS.quit:
                        log("(CURSES GAMEOVER):%s\n" % "this client pressed quit")
                        break


def displayEndOfGameMessages(gameOverMessage):
    width = 80
    ch = "-"
    line = ch * width
    gameOver = " GAME OVER "
    highscoreST = " HIGH SCORES "
    gameOverLine = ch * ((width-len(gameOver))//2) + gameOver + ch * ((width-len(gameOver) + 1)//2)
    highScoreLine = ch * ((width - len(highscoreST)) // 2) + highscoreST + ch * ((width - len(highscoreST) + 1) // 2)

    print line
    print gameOverLine
    print line
    print "You Were Killed by: %s"%gameOverMessage.get(GAMEOVER.kKiller, "Unknown")
    print "Your Score: %d"%gameOverMessage.get(GAMEOVER.kCurentScore, 0)

    # retrieve array of all properly formed score dictionaries
    highscores = [ score for score in gameOverMessage.get(GAMEOVER.kHighScores, [])
                   if all(k in score for k in (SCORES.kNames, SCORES.kScore, SCORES.kCauseOfDeath))]

    if highscores:

        NAME_HEADING = "NAMES"
        nameWidth = max(len(NAME_HEADING), max(len(str(sd[SCORES.kNames])) for sd in highscores))
        namePos = len("|| ")

        KILLER_HEADING = "KILLED BY"
        killerWidth = max(len(KILLER_HEADING), max(len(str(sd[SCORES.kCauseOfDeath])) for sd in highscores))
        killerPos = namePos + nameWidth + len(" | ")

        SCORE_HEADING = "SCORE"
        scoreWidth = max(len(SCORE_HEADING), max(len(str(sd[SCORES.kScore])) for sd in highscores))
        scorePos = width - len(" ||") - scoreWidth- 1

        templateLine = [" "] * width
        templateLine[:3] = "||"
        templateLine[-2:] = "||"
        templateLine[killerPos-2:killerPos-1] = "|"
        templateLine[scorePos-2:scorePos-1] = "|"

        categoryLine = list(templateLine)
        for st, pos in ( (NAME_HEADING,namePos), (KILLER_HEADING, killerPos), (SCORE_HEADING, scorePos)):
            categoryLine[pos:pos+len(st)] = st
        categoryLine = "".join(categoryLine)

        print ""
        print line
        print highScoreLine
        print line
        print categoryLine
        print line

        for scoreDict in highscores:
            scoreline = list(templateLine)
            for st, pos in ((scoreDict[SCORES.kNames], namePos),
                            (scoreDict[SCORES.kCauseOfDeath], killerPos),
                            (str(scoreDict[SCORES.kScore]), scorePos)):
                scoreline[pos:pos + len(st)] = st
            print "".join(scoreline)

        print line


def cursesEngine(networkPipe):
    gameWindow = startCurses()
    colorDict = initColors()

    gameWindow.resize(GAMEWINDOW_ROWS, GAMEWINDOW_COLS)
    chatDisplayWindow = curses.newwin(3, 80, 20, 0)
    chatEntryLine = curses.newwin(1, 79, 23, 0)
    chatMan = ChatManager(chatDisplayWindow, chatEntryLine, colorDict)

    localGame = gameState(graphicAssets.getAllAssets(), GAMEWINDOW_ROWS, GAMEWINDOW_COLS, colorDict)

    gameOverMessage = constantInputReadLoop(gameWindow, networkPipe, localGame, chatMan)
    exitCurses(gameWindow)
    log("(CURSES): curses screen exited\n")

    if gameOverMessage:
        displayEndOfGameMessages(gameOverMessage)
    else :
        print "Game exited by player,  Good Luck next time!"


