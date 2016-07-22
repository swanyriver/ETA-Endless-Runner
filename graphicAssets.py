import sys
import json
import glob
import os

class ParseAssetError(Exception):
    pass


#debugging method
def drawCharacterAndHitbox(drawing, hitbox):

    #convert hitbox to 2d array
    hitboxstring = ""
    for y in range(len(drawing)):
        hitboxstring += "\n" + drawing[y] + " | "
        for x in range(len(drawing[0])):
            hitboxstring += "#" if (y,x) in hitbox else " "
    return hitboxstring


#todo hitbox algo change to flood fill
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
                errorString = "drawings must be the same height, heights:" + str([len(d) for d in self.drawings]) + '\n'
                raise ParseAssetError(errorString)
            for s in d:
                if not (isinstance(s, str) or isinstance(s, unicode)):
                    raise ParseAssetError("drawings must contain arrays of strings")
                if len(s) != self.width:
                    errorString = "each line of drawing must be the same width, lineWidths:%s\n"%str([len(line) for line in d]) \
                                  + '\n'.join(d)
                    raise ParseAssetError(errorString)


        #detect hitbox on first drawing
        self.hitbox = getHitbox(self.height, self.width, self.drawings[0])


        #assert hitboxs are same for all drawings
        for d in self.drawings[1:]:
            if getHitbox(self.height, self.width, d) != self.hitbox:
                errorString = "hitbox for each drawing must be the same, because server will not know what animation frame is showing on each client"
                errorString += drawCharacterAndHitbox(self.drawings[0], self.hitbox)
                errorString += drawCharacterAndHitbox(d, getHitbox(self.height, self.width, d))
                raise ParseAssetError(errorString)



#returns one graphic asset instance, primarily for debugging, game should use factory method getAllAssets()
# used for web app testing of generated JSON over html interface
def CreateFromJSON(jsonString, name=None):
    try:
        data = json.loads(jsonString)
    except ValueError as e:
        raise ParseAssetError("failed to decode asset from json string\n" + str(e))
    asset = GraphicAsset(data, name)
    return asset


def createFromFileName(filename, debug=False):
    name = filename.split("/")[-1]
    name = name.split(".")[0]
    with open(filename, 'r') as assetFile:
        try:
            data = json.load(assetFile)
        except ValueError:
            if debug: print filename, " failed to decode json from file"
            return None
        try:
            asset = GraphicAsset(data, name)
            return asset
        except ParseAssetError as err:
            if debug: print filename, " failed to construct: ", err
            return None


def testOneAsset(jsonString):
    try:
        asset = CreateFromJSON(jsonString)
    except ParseAssetError as err:
        return err
    else:
        output = "GraphicAssets.py Successfully created asset from JSON\n"
        output += drawCharacterAndHitbox(asset.drawings[0], asset.hitbox)
        return output


#will return a dictionary of name:assets
DIRECTORY = "graphics"
FILE_TYPE = ".json"

def getAssetFileNames():
    return glob.glob("%s/*%s"%(DIRECTORY, FILE_TYPE))


def getAllAssets(debug = False):

    """
    :param debug: display verboase message on parse failure if true
    :rtype:dict[str, GraphicAsset]
    """

    graphicAssets = {g.name:g for g in
                     filter(None, (
                         createFromFileName(f, debug=debug) for f in getAssetFileNames()
                        ))
                     }

    if debug:
        print "%d assets parsed from files"%len(graphicAssets)
        print graphicAssets.keys()

    if not graphicAssets:
        errorString = "(CRITICAL ERROR): Graphic Library is empty CAUSE: " + \
            ("No %s files available in /%s folder or no %s folder"%(FILE_TYPE, DIRECTORY, DIRECTORY)
                if not getAssetFileNames()
                else "None of the %d asset files were properly formatted"%len(getAssetFileNames()))
        raise ParseAssetError(errorString)

    return graphicAssets


def getPlayerAsset(debug = False):
    """
    :param debug: display verboase message on parse failure if true
    :rtype: GraphicAsset
    """
    PLAYER_FILE_LOC = "graphics/reserved/player" + FILE_TYPE
    if not os.path.isfile(PLAYER_FILE_LOC):
        raise ParseAssetError("(CRITICAL ERROR): player graphic asset not present at: %s"%PLAYER_FILE_LOC)

    player = createFromFileName(PLAYER_FILE_LOC)

    if not player:
        raise ParseAssetError("(CRITICAL ERROR): player graphic asset could not be parsed")

    #todo make the return of this function the default param for the player __init__() and render side player entity
    return player


def displayGraphicLibrary():
    ga = getAllAssets().values() + [getPlayerAsset()]
    for g in ga:
        print "Asset: %s    H:%d  W:%d" % (g.name, g.height, g.width), "  <DEADLY>" if g.deadly else ""
        print "\nDRAWING AND HIBOX:"
        print drawCharacterAndHitbox(g.drawings[0], g.hitbox)

        if len(g.drawings) > 1:
            print "\nANIMATION FRAMES:\n"
            PADDING = 4
            perRow = 80 // (g.width + PADDING)

            leftIndex = 0
            rightIndex = 0
            while rightIndex < len(g.drawings):
                rightIndex += perRow
                leftIndex = rightIndex - perRow

                for row in range(g.height):
                    print (" " * PADDING).join(
                        g.drawings[frame][row] for frame in range(leftIndex, min(rightIndex, len(g.drawings)))
                    )
                print ""

        print "--------------------------------------"
        print "--------------------------------------"



if __name__ == '__main__':

    if "-d" in sys.argv or "-display" in sys.argv:
        displayGraphicLibrary()

    if len(sys.argv) > 1:
        pass
        #todo read and display one asset in curses, with color and hitbox
    else:
        getAllAssets(debug=True)
        getPlayerAsset(debug=True)
