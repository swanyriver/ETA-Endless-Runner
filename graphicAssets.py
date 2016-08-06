import sys
import json
import glob
import os

VERTWALLMAXWIDTH = 5
HORIZWALLMAXHEIGHT = 4

class ParseAssetError(Exception):
    pass


class GraphicsLibrary(dict):
    def __init__(self, d):
        super(GraphicsLibrary, self).__init__(d)

    def getCategories(self):
        allCategories = set(g.category for g in self.values() if g.category)
        # return only viable categories to draw a room,  must have both usable decor and enemies
        return [c for c in allCategories if c and
                [d for d in self.getDecorations(c) if d.width <= VERTWALLMAXWIDTH] and
                [d for d in self.getDecorations(c) if d.height <= HORIZWALLMAXHEIGHT] and
                self.getBadGuys(c)]

    def getAllDecorations(self):
        return [g for g in self.values() if not g.deadly]

    def getAllBadGuys(self):
        return [g for g in self.values() if g.deadly]

    def getDecorations(self, category):
        return [g for g in self.values() if not g.deadly and g.category == category]

    def getBadGuys(self, category):
        return [g for g in self.values() if g.deadly and (g.category == category or g.category == "Enemy")]


#debugging method
def drawCharacterAndHitbox(drawing, hitbox):

    #convert hitbox to 2d array
    hitboxstring = ""
    for y in range(len(drawing)):
        hitboxstring += "\n" + drawing[y] + " | "
        for x in range(len(drawing[0])):
            hitboxstring += "#" if (y,x) in hitbox else " "
    return hitboxstring


def getNeighborTuples(y,x):
    return [
        (y-1, x), (y+1, x),
        (y, x-1), (y, x+1)
    ]


def getHitbox(height, width, drawing):
    # FloodFill algorithm for defining drawings hitbox
    allPixels = set([(y, x) for y in range(height) for x in range(width)])

    safe = set(
        [(-1,x) for x in range(width)] +
        [(height,x) for x in range(width)] +
        [(y, -1) for y in range(height)] +
        [(y, width) for y in range(height)]
    )

    search = set(safe)

    while search:
        n = search.pop()
        neighbors = [(y,x) for y,x in getNeighborTuples(*n) if
                     0 <= y < height and 0 <= x < width and
                     drawing[y][x] == " " and
                     (y,x) not in safe]

        safe.update(neighbors)
        search.update(neighbors)

    # after flood fill all reachable space characters are marked safe, hitbox will be remaining
    # Htibox may include enclosed space characters (intended)
    # Htibox may not be contiguous (intended)
    return allPixels.difference(safe)

def stringArrayProperlyFormed(arr, w, h):
    if type(arr) is not list or len(arr)<h:
        return False
    return all((isinstance(line, str) or isinstance(line, unicode)) and len(line) == w for line in arr)


class GraphicAsset():
    kDeadly = "deadly" #Boolean
    kDrawings = "drawings" #array of arrays of strings
    kCategory = "category"
    kColors = "colors"
    kBackColor = "backColors"
    kBlack = "K"
    kRed = "R"
    kGreen = "G"
    kYellow = "Y"
    kBlue = "B"
    kMagenta = "M"
    kCyan = "C"
    kWhite = "W"

    def __init__(self, loaded, name):
        self.name = name
        self.colorFrames = None
        self.backgroundFrames = None
        self.category = loaded.get(GraphicAsset.kCategory, None) or None
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
                errorString += "\n\n"
                errorString += drawCharacterAndHitbox(d, getHitbox(self.height, self.width, d))
                raise ParseAssetError(errorString)

        #parse color arrays  #forginingly
        if GraphicAsset.kColors in loaded:
            if len(loaded[GraphicAsset.kColors]) == len(self.drawings) and \
                    all(stringArrayProperlyFormed(l, self.width, self.height) for l in loaded[GraphicAsset.kColors]):
                self.colorFrames = loaded[GraphicAsset.kColors]
            else:
                raise ParseAssetError("json file " + GraphicAsset.kColors + " field improperly defined")

        if GraphicAsset.kBackColor in loaded:
            if len(loaded[GraphicAsset.kBackColor]) == len(self.drawings) and \
                    all(stringArrayProperlyFormed(l, self.width, self.height) for l in loaded[GraphicAsset.kBackColor]):
                self.backgroundFrames = loaded[GraphicAsset.kBackColor]
            else:
                raise ParseAssetError("json file " + GraphicAsset.kBackColor + " field improperly defined")





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
        return False, str(err)
    else:
        output = "GraphicAssets.py Successfully created asset from JSON\n"
        output += drawCharacterAndHitbox(asset.drawings[0], asset.hitbox)
        return True, str(output)


#will return a dictionary of name:assets
DIRECTORY = "graphics"
FILE_TYPE = ".json"


def getAssetFileNames():
    return glob.glob("%s/*%s"%(DIRECTORY, FILE_TYPE))


def getAllAssets(debug = False):

    """
    :param debug: display verboase message on parse failure if true
    :rtype:GraphicsLibrary
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

    return GraphicsLibrary(graphicAssets)


def getReservedAsset(FILE_LOC, debug = False):
    if not os.path.isfile(FILE_LOC):
        raise ParseAssetError("(CRITICAL ERROR): player graphic asset not present at: %s" % FILE_LOC)
    asset = createFromFileName(FILE_LOC)
    if not asset:
        raise ParseAssetError("(CRITICAL ERROR): player graphic asset could not be parsed")

    return asset


def getPlayerAsset(debug = False):
    """
    :param debug: display verboase message on parse failure if true
    :rtype: GraphicAsset
    """
    PLAYER_FILE_LOC = DIRECTORY + "/reserved/player" + FILE_TYPE
    return getReservedAsset(PLAYER_FILE_LOC)


def getVertBlocker(debug = False):
    """
    :param debug: display verboase message on parse failure if true
    :rtype: GraphicAsset
    """
    blockerFile = DIRECTORY + "/reserved/vertBlocker" + FILE_TYPE
    return getReservedAsset(blockerFile)


def getHorizBlocker(debug = False):
    """
    :param debug: display verboase message on parse failure if true
    :rtype: GraphicAsset
    """
    blockerFile = DIRECTORY + "/reserved/horizBlocker" + FILE_TYPE
    return getReservedAsset(blockerFile)


def displayGraphicLibrary(ga=None):
    ga = ga or getAllAssets().values() + [getPlayerAsset()]

    print "\n\n------------------------------------------"
    print "--------- FULL GRAPHICS LIBRARY ----------"
    print "------------------------------------------"

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

        print "\n\nCATEGORIES:"
        for c in set(g.category for g in ga):
            assetsInCategory = [g for g in ga if g.category == c]
            print "(%d)"%len(assetsInCategory), c, "\t",
            print ["<%s>"%g.name if g.deadly else g.name for g in assetsInCategory]

        print ""
        #create galibraryobject
        gaL = GraphicsLibrary({g.name:g for g in ga} )
        print "catagories with sufficient decor and enemies:", gaL.getCategories()



if __name__ == '__main__':

    if "-d" in sys.argv or "-display" in sys.argv:
        displayGraphicLibrary()
        exit()

    elif "-f" in sys.argv and len(sys.argv) > sys.argv.index("-f"):
        print "testing file %s"%sys.argv[sys.argv.index("-f") + 1]

        asset = createFromFileName(sys.argv[sys.argv.index("-f") + 1])

        if not asset:
            print "failed to load from file"
            exit(1)

        import cursesIO
        import gameEntities
        from multiprocessing import  Process, Pipe

        cursesEnd, networkEnd = Pipe(duplex=True)
        cursesProcess = Process(target=cursesIO.cursesEngine, args=(cursesEnd,))
        cursesProcess.start()
        networkEnd.send(gameEntities.JSONforNetwork(screen=[gameEntities.gameEntity(asset,0,0)]))

    else:
        graphics = getAllAssets(debug=True)
        player = getPlayerAsset(debug=True)
        #displayGraphicLibrary(ga=(graphics.values() + [player]))
