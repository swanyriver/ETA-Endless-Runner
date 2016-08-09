kSCREEN = "screen"
kCHAR = "charPos"
kGAMEOVER = "gameOver"

# sadly there is no Enum class or pattern in python 2.x so this class will need to be used with extreme caution
class ACTIONS():
    up = "w"
    down = "s"
    left = "a"
    right = "d"
    quit = "q"
    chat = "/"
    name = "#"


class ENTITY():
    kGraphicAsset = "ga"
    kX = "x"
    kY = "y"
ENTITYKEYS = {ENTITY.kGraphicAsset: unicode, ENTITY.kX: int, ENTITY.kY: int}


class GAMEOVER():
    kCurentScore = "score"
    kKiller = "killer"
    kHighScores = "highScores"


class SCORES():
    kNames = "names"
    kScore = "score"
    kCauseOfDeath = "killer"