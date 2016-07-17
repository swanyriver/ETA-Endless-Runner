import cursesIO
from multiprocessing import Process, Pipe
from log import log
import random
import graphicAssets
import gameEntities
import time

#todo move to dummy server
def getRandomWorld(asset):
    NUM_GEN = 6
    entities = []
    availables = filter(lambda k:k!= "character", assets.keys())
    for k in [random.choice(availables) for _ in range(NUM_GEN)]:
        y, x = random.randint(0, 20 - 2), random.randint(0, 80 - 1)
        entities.append(gameEntities.gameEntity(assets[k], y, x))

    log("JSON OF ENTITIES:\n" + gameEntities.JSONforNetwork(screen=entities))

    return entities

#temp test
assets = graphicAssets.getAllAssets()

chary,charx = 10, 40

cursesEnd, networkEnd = Pipe(duplex=True)
cursesProcess = Process(target=cursesIO.cursesEngine, args=(cursesEnd,))
cursesProcess.start()

#send first message
networkEnd.send(gameEntities.JSONforNetwork(screen=getRandomWorld(assets),
                                            charX=charx, charY=chary))

i = 0
SCREEN_REFRESH = 1
lastRefresh = 0

while cursesProcess.is_alive():

    if networkEnd.poll():
        msg = networkEnd.recv()
        log("(DUMMY NET MSG-FROM-CURSES):" + str(type(msg)) + str(msg) + "\n")

    if time.time() - lastRefresh < SCREEN_REFRESH:
        continue

    #else
    lastRefresh = time.time()
    i += 1

    charx += random.randint(-2,2)
    chary += random.randint(-2,2)

    if i % 10 == 0:
        networkEnd.send(gameEntities.JSONforNetwork(screen=getRandomWorld(assets),
                                                    charX=charx, charY=chary))
    else:
        networkEnd.send(gameEntities.JSONforNetwork(screen=getRandomWorld(assets)))

