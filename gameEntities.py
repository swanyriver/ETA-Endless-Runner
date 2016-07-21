from collections import namedtuple
import graphicAssets
import json
from networkKeys import *

#todo add color
Pixel = namedtuple("pixel", ['y', 'x', 'char'])

class gameEntity(object):
    def __init__(self, graphicAsset, y, x):
        self.graphic = graphicAsset
        self.y = y
        self.x = x

    ########################################
    #methods to be used by server game side
    #########################################

    def setYX(self, y, x):
        self.y = y
        self.x = x

    def getLeftBound(self):
        return self.x
    def getRightBound(self):
        return self.x + self.getWidth() - 1

    def getTopBound(self):
        return self.y

    def getBottomBound(self):
        return self.y + self.getHeight() - 1

    def getBoundingRect(self):
        return self.getTopBound(), self.getLeftBound(), self.getBottomBound(), self.getRightBound()

    def isDeadly(self):
        return self.graphic.deadly

    ########################################
    #methods used by client/render side
    ########################################
    def getYX(self):
        return self.y, self.x

    #todo add color
    #todo choose drawing index by animation sequence
    def getDrawing(self):
        return [Pixel(y + self.y, x + self.x, ord(self.graphic.drawings[0][y][x]))
                for y in range(self.graphic.height)
                for x in range(self.graphic.width)
                if self.graphic.drawings[0][y][x] != " "]

    def getHeight(self):
        return self.graphic.height

    def getWidth(self):
        return self.graphic.width

    def getDeltaHitbox(self):
        return [(y + self.y, x + self.x) for y, x in self.graphic.hitbox]

    def __repr__(self):
        return "%s at YX:%d,%d %s" % (self.graphic.name, self.y, self.x, ("<DEADLY>" if self.isDeadly() else ""))



#screen should be array of gameEntity instances
#char Y and X are ints
#gameOver should be a dictionary with k:v needed at end of game reasonForEnd (death, other client), score
def JSONforNetwork(screen=None, charY=None, charX=None, gameOver=None):
    output = {}
    if screen:
        output[kSCREEN] = [{"graphicAsset":e.graphic.name, "x": e.x, "y": e.y} for e in screen]
    if charX is not None and charY is not None:
        output[kCHAR] = {'y':charY, 'x':charX}
    if gameOver:
        output[kGAMEOVER] = gameOver
    return json.dumps(output) + "\n"

# entities = array of gameEntity instances, player is instance of game_state.Player
COLLIDED = 1
DEAD = -1

def checkCollision(entities, player):
    """
    :type entities: [gameEntity]
    :type player: gameEntity
    :return : tuple (COLLIDED | DEAD | None,  <gameEntity> collided with | None)
    """

    #todo create hitbox proccessing class to store calced hitboxes and compare
    #todo only re-calc hitbox map when entitys have changed, and compare entity list before regen hitbox map

    # y,x points are added to a dictionary as keys, with values being entity that is occupying that pixel
    #   added in order as order defines draw & collision order with last item in array being drawn on-top and first to
    #   collide with player,  a dangerous object with a save object drawn entirely over it (safe object has higher
    #   index in array) will be entirely invisible and safe for the player to collide with.
    collionsMap = {}
    for e in entities:
        collionsMap.update(
            {point: e for point in e.getDeltaHitbox()}
        )

    # create a set of distinct game entities that the players hitbox is overlapping presently
    collidedWith = list(set(collionsMap.get(point) for point in player.getDeltaHitbox() if point in collionsMap))

    # players new position does not touch any deadly or non-deadly entities
    if not collidedWith:
        return None, None

    # player has colided with something deadly
    if any(e.isDeadly() for e in collidedWith):
        whoKilledPlayer = filter(lambda c: c.isDeadly(), collidedWith)
        otherCollisions = filter(lambda c: not c.isDeadly(), collidedWith)
        print "(GAME-STATE COLLISION): player was killed by the entitie(s): ", whoKilledPlayer, \
            ((",   player also collided with: " + str(otherCollisions)) if otherCollisions else "")

        #todo is this the best way of choosing the killer,  should we report all that had a hand in players demise
        return DEAD, whoKilledPlayer[0]

    # player has collided with something not deadly
    else:
        print "(GAME-STATE COLLISION): player collided with", collidedWith
        return COLLIDED, collidedWith[0]
