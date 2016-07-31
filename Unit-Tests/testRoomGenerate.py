from multiprocessing import Process, Pipe
import time

# For importing our files from outer directory
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import game_state
import gameFunctions
import cursesIO


# For silencing log output from curses
import os
import sys
f = open(os.devnull, 'w')
sys.stderr = f


# in Seconds
REFRESH_INTERVAL = 4


cursesEnd, networkEnd = Pipe(duplex=True)
cursesProcess = Process(target=cursesIO.cursesEngine, args=(cursesEnd,))
cursesProcess.start()

game = game_state.Gamestate()
networkEnd.send(game.get_update())


lastRefresh = time.time()
while cursesProcess.is_alive():
    if time.time() - lastRefresh >= REFRESH_INTERVAL:
        lastRefresh = time.time()
        game.entities = gameFunctions.getNewGameRoom(game)
        networkEnd.send(game.get_update())
    else:
        pass
