from collections import namedtuple
import graphicAssets
import json

#todo add color
pixel = namedtuple("pixel", ['y','x','char'])

class gameEntity():
    def __init__(self, graphicAsset, y, x):
        self.graphic = graphicAsset
        self.y = y
        self.x = x

    #methods to be used by server game side

    #can be used to make a json of an array of these entities
    def __repr__(self):
        return str({"graphicAsset":self.graphic.name, "x":self.x, "y":self.y}).replace("\'","\"")

    def setYX(self, y, x):
        self.y = y
        self.x = x

    #methods used by client/render side
    def getYX(self):
        return self.y, self.x

    #todo add color
    #todo choose drawing index by animation sequence
    def getDrawing(self):
        return [pixel(y, x, self.graphic.drawings[0][y][x])
                for y in range(self.graphic.height)
                for x in range(self.graphic.width)
                if self.graphic.drawings[0][y][x] != " "]


# class screen():
#     DEAD =(-1,-1)
#     def __init__(self, entities):
#         #creates a map of hitboxes
#
#



#for testing
if __name__ == '__main__':
    import random
    import cursesIO
    import log

    assets = graphicAssets.getAllAssets()
    screen = []
    for k in [random.choice(assets.keys()) for _ in range(6)]:
        y,x = random.randint(0, 20 - assets[k].height - 1), random.randint(0, 80 - assets[k].width - 1)
        screen.append(gameEntity(assets[k], y, x))

    log.log(str(screen))

    cursesIO.createScreenArray(str(screen), assets)


