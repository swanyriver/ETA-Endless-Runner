kSCREEN = "screen"
kCHAR = "charPos"
kGAMEOVER = "gameOver"
ENTITYKEYS = {"graphicAsset": unicode, "x": int, "y": int}

# sadly there is no Enum class or pattern in python 2.x so this class will need to be used with extreme caution
class ACTIONS():
    up = "w"
    down = "s"
    left = "a"
    right = "d"
    quit = "q"
    chat = "/"

