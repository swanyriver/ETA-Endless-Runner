import sys
import json
import os
import glob

class ParseAssetError(Exception):
    pass

#debuggin method
def drawCharacterAndHitbox(drawing, hitbox):

    #convert hitbox to 2d array
    hitboxstring = ""
    for y in range(len(drawing)):
        hitboxstring += "\n" + drawing[y] + " | "
        for x in range(len(drawing[0])):
            hitboxstring += "#" if (y,x) in hitbox else " "
    return hitboxstring


def getHitbox(height, width, drawing):
    hitbox = set([(y, x) for y in range(height) for x in range(width)])
    # send probes from outer edge removing cords from hitbox
    # top to bottom
    for y in range(height):
        for x in range(width):
            if drawing[y][x] == " " and (y,x) in hitbox:
                hitbox.remove((y,x))
            else:
                break
        for x in reversed(range(width)):
            if drawing[y][x] == " " and (y, x) in hitbox:
                hitbox.remove((y, x))
            else:
                break

    # left to right
    for x in range(width):
        for y in range(height):
            if drawing[y][x] == " " and (y, x) in hitbox:
                hitbox.remove((y, x))
            else:
                break
        for y in reversed(range(height)):
            if drawing[y][x] == " " and (y, x) in hitbox:
                hitbox.remove((y, x))
            else:
                break

    return hitbox


class GraphicAsset():
    kDeadly = "deadly" #Boolean
    kDrawings = "drawings" #array of arrays of strings
    kColors = "colors" #array of arrays, todo define pattern for declaring, assert same as drawings array

    def __init__(self, loaded, name):
        self.name = name
        #for k in [GraphicAsset.kDeadly, GraphicAsset.kDrawings, GraphicAsset.kColors]:
        for k in [GraphicAsset.kDeadly, GraphicAsset.kDrawings]:
            if k not in loaded:
                raise ParseAssetError("json file missing required field: " + k)

        self.deadly = loaded[GraphicAsset.kDeadly]
        if type(self.deadly) is not bool:
            raise ParseAssetError("json file deadly field improperly defined")

        self.drawings = loaded[GraphicAsset.kDrawings]
        if type(self.drawings) is not list or len(self.drawings)<1:
            raise ParseAssetError("json file drawings field improperly defined")
        self.height = len(self.drawings[0])
        self.width = len(self.drawings[0][0]) if self.height else 0

        if not self.height or not self.width:
            raise  ParseAssetError("drawings arrays must not be empty")

        #verify drawings are uniformly defined (same height and width for each and each string is the same lengt
        for d in self.drawings:
            if not isinstance(d, list):
                raise ParseAssetError("drawings must contain arrays of strings")
            if len(d) != self.height:
                raise ParseAssetError("drawings must be the same height")
            for s in d:
                if not (isinstance(s, str) or isinstance(s, unicode)):
                    raise ParseAssetError("drawings must contain arrays of strings")
                if len(s) != self.width:
                    raise ParseAssetError("each line of drawing must be the same width")

        #detect hitbox on first drawing
        self.hitbox = getHitbox(self.height, self.width, self.drawings[0])


        #assert hitboxs are same for all drawings
        for d in self.drawings[1:]:
            if getHitbox(self.height, self.width, d) != self.hitbox:
                errorString = "hitbox for each drawing must be the same, because server will not know what animation frame is showing on each client"
                errorString += drawCharacterAndHitbox(self.drawings[0], self.hitbox)
                errorString += drawCharacterAndHitbox(d, getHitbox(self.height, self.width, d))
                raise ParseAssetError(errorString)

#will return a dictionary of name:assets
def getAllAssets(debug = False):

    graphicAssets = {}

    for f in glob.glob("graphics/*.json"):
        name = f.split("/")[-1]
        name = name.split(".")[0]
        with open(f, 'r') as assetFile:
            try:
                data = json.load(assetFile)
            except ValueError:
                if debug: print f, " failed to decode json"
                continue
            try:
                asset = GraphicAsset(data, name)
                graphicAssets[name] = asset
            except ParseAssetError as err:
                if debug: print f, " failed to construct: ", err

    if debug:
        print "%d assets parsed from files"%len(graphicAssets)
        print graphicAssets.keys()

    return graphicAssets


if __name__ == '__main__':
    if len(sys.argv) > 1:
        pass
        #todo read and display one asset in curses, with color and hitbox
    else:
        getAllAssets(debug=True)
