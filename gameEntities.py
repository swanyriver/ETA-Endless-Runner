from collections import namedtuple
import graphicAssets
import json

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
    kSCREEN = "screen"
    kCHAR = "charPos"
    kGAMEOVER = "gameOver"
    output = {}
    if screen:
        output[kSCREEN] = [{"graphicAsset":e.graphic.name, "x": e.x, "y": e.y} for e in screen]
    if charX is not None and charY is not None:
        output[kCHAR] = {'y':charY, 'x':charX}
    if gameOver:
        output[kGAMEOVER] = gameOver
    return json.dumps(output) + "\n"

#for testing
#if __name__ == '__main__':
    #todo remove invalidated
    # import random
    # import cursesIO
    # import log
    #
    # assets = graphicAssets.getAllAssets()
    # entities = []
    # for k in [random.choice(assets.keys()) for _ in range(6)]:
    #     y,x = random.randint(0, 20 - assets[k].height - 1), random.randint(0, 80 - assets[k].width - 1)
    #     entities.append(gameEntity(assets[k], y, x))
    #
    # log.log(str(entities) + '\n')
    #
    # cursesEntities = cursesIO.createScreenArray(str(entities), assets)
    # cursesScreen = cursesIO.startCurses()
    # cursesIO.renderEntities(cursesScreen,cursesEntities)
    #
    # while 1:
    #     char_in = cursesScreen.getch()
    #     if char_in == ord('q'): break
    #
    # cursesIO.exitCurses(cursesScreen)

