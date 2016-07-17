from multiprocessing import Process, Pipe
from log import log
import random
import graphicAssets
import gameEntities
import time
from networkKeys import *


class DummyGameServer():
    # todo move to dummy server
    def getRandomWorld(self):
        NUM_GEN = 6
        entities = []
        availables = filter(lambda k: k != "character", self.GraphicAssets.keys())
        for k in [random.choice(availables) for _ in range(NUM_GEN)]:
            y, x = random.randint(0, 20 - 2), random.randint(0, 80 - 1)
            entities.append(gameEntities.gameEntity(self.GraphicAssets[k], y, x))

        # log("JSON OF ENTITIES:\n" + gameEntities.JSONforNetwork(screen=entities))
        return entities

    WORLD_REFRESH = 10
    def __init__(self):
        self.GraphicAssets = graphicAssets.getAllAssets()
        self.refreshCountdown = 0
        self.charY = 10
        self.charX = 20

    def moveLeft(self):
        self.charX -= 1

    def moveRight(self):
        self.charX += 1

    def moveUp(self):
        self.charY -=1

    def moveDown(self):
        self.charY +=1

    def getGameUpdate(self):
        self.refreshCountdown -= 1
        if self.refreshCountdown <= 0:
            self.refreshCountdown = DummyGameServer.WORLD_REFRESH
            return gameEntities.JSONforNetwork(screen=self.getRandomWorld(), charX=self.charX, charY=self.charY)
        else:
            return gameEntities.JSONforNetwork(charX=self.charX, charY=self.charY)
