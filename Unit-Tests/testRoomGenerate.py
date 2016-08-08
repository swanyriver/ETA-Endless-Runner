from multiprocessing import Process, Pipe
import time

import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from gameFunctions import *
from graphicAssets import VERTWALLMAXWIDTH, HORIZWALLMAXHEIGHT
import game_state
import gameFunctions
import cursesIO


# For silencing log output from curses
import os
import sys
f = open(os.devnull, 'w')
sys.stderr = f

# In seconds
REFRESH_INTERVAL = 1.5
INCREASE_ENEMY_COUNT = 3


def getRandomEntry(maxX, maxY, playerWidth, playerHeight):
    side = random.choice(SIDES)
    if side == NORTH:
        return -1, random.randint(VERTWALLMAXWIDTH, maxX-VERTWALLMAXWIDTH - playerWidth)
    if side == SOUTH:
        return maxY-2, random.randint(VERTWALLMAXWIDTH, maxX-VERTWALLMAXWIDTH - playerWidth)

    if side == WEST:
        return random.randint(HORIZWALLMAXHEIGHT, maxY - HORIZWALLMAXHEIGHT - playerHeight), -2
    if side == EAST:
        return random.randint(HORIZWALLMAXHEIGHT, maxY - HORIZWALLMAXHEIGHT - playerHeight), maxX-2


cursesEnd, networkEnd = Pipe(duplex=True)
cursesProcess = Process(target=cursesIO.cursesEngine, args=(cursesEnd,))
cursesProcess.start()

game = game_state.Gamestate()
networkEnd.send(game.get_update())

countdown_to_enemy = INCREASE_ENEMY_COUNT
lastRefresh = time.time()
while cursesProcess.is_alive():
    if time.time() - lastRefresh >= REFRESH_INTERVAL:
        lastRefresh = time.time()

        countdown_to_enemy -= 1
        if not countdown_to_enemy:
            countdown_to_enemy = INCREASE_ENEMY_COUNT
            game.numBadGuysToPlace += 1

        game.player.setYX(*getRandomEntry(game.grid.width, game.grid.height, game.player.getWidth(), game.player.getHeight()))

        game.entities = gameFunctions.getNewGameRoom(game)
        networkEnd.send(game.get_update())
    else:
        pass
