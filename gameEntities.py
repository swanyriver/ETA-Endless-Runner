from collections import namedtuple
import graphicAssets
import json
from networkKeys import *

#todo add color
Pixel = namedtuple("pixel", ['y', 'x', 'char'])

class gameEntity():
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
