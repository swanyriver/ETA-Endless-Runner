import random
import gameEntities
import itertools
from log import log

# todo determine if character has entered new screen and update game layout
#return None if player still on same screen
#return (y,x) tuple for player on new screen
def playerLeftScreen(Game):
    return None

#todo generate random screens
NORTH = 0
SOUTH = 1
EAST = 2
WEST = 3
SIDES = [NORTH, SOUTH, EAST, WEST]
SIDENAMES = {NORTH:"NORTH", SOUTH:"SOUTH", EAST:"EAST", WEST:"WEST"}
VERTWALLMAXWIDTH = 5
HORIZWALLMAXHEIGHT = 4
GATESZIE = 1.25

def playerOnSide(player, grid):
    """
    :type player: game_state.player
    :param grid: game_state.Grid
    :return:
    """
    y,x = player.getYX()
    if y <= 0:
        return NORTH
    elif y >= grid.height - player.getHeight():
        return SOUTH
    elif x <= 0:
        return WEST
    elif x >= grid.width - player.getWidth():
        return EAST


def gateOnSide(gate, grid):
    """
    :type player: game_state.player
    :param grid: game_state.Grid
    :return:
    """
    y,x = gate
    if y <= 0:
        return NORTH
    elif y >= grid.height:
        return SOUTH
    elif x <= 0:
        return WEST
    elif x >= grid.width:
        return EAST


def getVertWall(asset, xpos, ystart, yend, withGate=False, withPlayer=False, player=None, gates=None):
    if not withGate and not withPlayer:
        return [gameEntities.gameEntity(asset, y, xpos) for y in range(ystart, yend+1, asset.height)]
    output = []
    if withPlayer:
        playerY, playerX = player.getYX()
        while ystart + asset.height < playerY:
            output.append(gameEntities.gameEntity(asset, ystart, xpos))
            ystart += asset.height
        ystart= playerY + player.getHeight()
        while ystart < yend:
            output.append(gameEntities.gameEntity(asset, ystart, xpos))
            ystart += asset.height
        return output

    if withGate:
        while yend - ystart - asset.height - 1 > player.getHeight() * GATESZIE:
            if random.choice(["up","down"]) == "up":
                output.append(gameEntities.gameEntity(asset, ystart, xpos))
                ystart += asset.height
            else:
                yend -= asset.height
                output.append(gameEntities.gameEntity(asset, yend, xpos))

        gates.append((ystart, xpos if xpos == 0 else xpos + asset.width))
        return output


def getHorizWall(asset, ypos, xstart, xend, withGate=False, withPlayer=False, player=None, gates=None, horizWidth=None):
    if not withGate and not withPlayer:
        return [gameEntities.gameEntity(asset, ypos, x) for x in range(xstart, xend + 1, asset.width)]
    output = []
    if withPlayer:
        playerY, playerX = player.getYX()
        while xstart + asset.width < playerX:
            output.append(gameEntities.gameEntity(asset, ypos, xstart))
            xstart += asset.width
        xstart = playerX + player.getWidth()
        while xstart < xend:
            output.append(gameEntities.gameEntity(asset, ypos, xstart))
            xstart += asset.width
        return output

    if withGate:
        # ensure gate is not in corner
        # todo, if there were very long elements this could trap the player
        while xstart < horizWidth:
            output.append(gameEntities.gameEntity(asset, ypos, xstart))
            xstart += asset.width
        rightCorner = xend - horizWidth
        while xend > rightCorner:
            xend -= asset.width
            output.append(gameEntities.gameEntity(asset, ypos, xend))

        while xend - xstart - asset.width - 1 > player.getWidth() * GATESZIE:
            if random.choice(["left", "right"]) == "left":
                output.append(gameEntities.gameEntity(asset, ypos, xstart))
                xstart += asset.width
            else:
                xend -= asset.width
                output.append(gameEntities.gameEntity(asset, ypos, xend))

        gates.append((ypos if ypos == 0 else ypos + asset.height, xstart))
        return output


def inclusiveRange(a, b):
    a,b = sorted((a,b))
    return range(a,b+1)


def getPlayerPath(player, outGate, grid, wallWidth, wallHeight):
    exitY, exitX = outGate
    playerY, playerX = player.getYX()
    playerSide = playerOnSide(player, grid)
    exitSide = gateOnSide(outGate, grid)

    log("(GAME-GEN) player on: %s (%d,%d)  exit on: %s (%d,%d)\n"%(SIDENAMES[playerSide], playerY, playerX,
                                                                   SIDENAMES[exitSide], exitY, exitX))

    path = []
    #get player clear of wall
    if playerSide == NORTH:
        path.extend((y, playerX) for y in range(playerY, wallHeight+1))
        playerY = wallHeight
    elif playerSide == SOUTH:
        path.extend((y, playerX) for y in range(playerY, grid.height-wallHeight-player.getHeight()-1, -1))
        playerY = grid.height-wallHeight-player.getHeight()
    elif playerSide == WEST:
        path.extend((playerY, x) for x in range(playerX, wallWidth+1))
        playerX = wallWidth
    elif playerSide == EAST:
        path.extend((playerY, x) for x in range(playerX, grid.width-wallWidth-player.getWidth()-1, -1))
        playerX = grid.width-wallWidth-player.getWidth()

    #reseve of exit path for player
    if exitSide == NORTH:
        path.extend((y, exitX) for y in inclusiveRange(0 - player.getHeight(), wallHeight))
        exitY = wallHeight
    elif exitSide == SOUTH:
        path.extend((y, exitX) for y in inclusiveRange(grid.height, grid.height - wallHeight - player.getHeight()))
        exitY = grid.height - wallHeight - player.getHeight()
    elif exitSide == WEST:
        path.extend((exitY, x) for x in inclusiveRange(0 - player.getWidth(), wallWidth))
        exitX = wallWidth
    elif exitSide == EAST:
        path.extend((exitY, x) for x in inclusiveRange(grid.width, grid.width - wallWidth - player.getWidth()))
        exitX = grid.width - wallWidth - player.getWidth()

    genInnerPath = random.choice((True,False))

    genInnerPath = True #todo remove

    #Generate path from opposite walls
    if sorted([playerSide, exitSide]) == sorted([NORTH, SOUTH]):
        if genInnerPath:
            pivotPoint = random.randint(wallHeight, grid.height - wallHeight - player.getHeight())
            path.extend( (y, playerX) for y in inclusiveRange(playerY, pivotPoint) )
            path.extend( (pivotPoint, x) for x in inclusiveRange(playerX, exitX) )
            path.extend( (y, exitX) for y in inclusiveRange(pivotPoint, exitY))
            return path
        else:
            #outer path to opposite gate
            #go left or right
            if random.choice("lr") == "l":
                vertPathX = wallWidth
            else:
                vertPathX = grid.width - wallWidth - player.getWidth()

            path.extend((playerY, x) for x in inclusiveRange(playerX, vertPathX))
            path.extend((y, vertPathX) for y in inclusiveRange(playerY, exitY))

    if sorted([playerSide, exitSide]) == sorted([EAST, WEST]):
        if genInnerPath:
            pivotXPoint = random.randint(wallWidth, grid.width - wallWidth - player.getWidth())
            path.extend( (playerY, x) for x in inclusiveRange(playerX, pivotXPoint))
            path.extend( (y, pivotXPoint) for y in inclusiveRange(playerY, exitY))
            path.extend( (exitY, x) for x in inclusiveRange(pivotXPoint, exitX))
            return path
        else:
            return path #todo implement outer

    # Generate cornered path
    else:
        return path #todo implement corner paths





def getNewGameRoom(Game):
    """
    :type Game: game_state.Gamestate
    :return:
    """

    decor = Game.gaLibrary.getAllDecorations()
    enimies = Game.gaLibrary.getAllBadGuys()
    entities = []



    #############################
    #### CREATE WALLS & GATES ###
    #############################
    vertWallDecor = random.choice([d for d in decor if d.width <= VERTWALLMAXWIDTH])
    horizWallDecor = random.choice([d for d in decor if d.height <= HORIZWALLMAXHEIGHT])
    playersSide = playerOnSide(Game.player, Game.grid)
    sidesWithGates = random.sample([side for side in SIDES if side != playersSide], random.randint(1, 3))

    opposite = {NORTH:SOUTH, SOUTH:NORTH, EAST:WEST, WEST:EAST} #todo remove this test
    sidesWithGates = [opposite.get(playersSide, NORTH)] #todo remove this test

    gates = []
    #west
    entities.extend(getVertWall(vertWallDecor, 0, horizWallDecor.height, Game.grid.height - horizWallDecor.height,
                                withGate=WEST in sidesWithGates, withPlayer= WEST == playersSide, player=Game.player,
                                gates=gates))
    #east
    entities.extend(getVertWall(vertWallDecor, Game.grid.width - vertWallDecor.width,
                                horizWallDecor.height, Game.grid.height - horizWallDecor.height,
                                withGate=EAST in sidesWithGates, withPlayer=EAST == playersSide, player=Game.player,
                                gates=gates))
    #north
    entities.extend(getHorizWall(horizWallDecor, 0, 0, Game.grid.width,
                                withGate=NORTH in sidesWithGates, withPlayer=NORTH == playersSide, player=Game.player,
                                gates=gates, horizWidth=horizWallDecor.width))
    #south
    entities.extend(getHorizWall(horizWallDecor, Game.grid.height - horizWallDecor.height, 0, Game.grid.width,
                                 withGate=SOUTH in sidesWithGates, withPlayer=SOUTH == playersSide, player=Game.player,
                                 gates=gates, horizWidth=horizWallDecor.width))


    ##########################################################
    ## RESERVE PATH FROM PLAYER TO AT LEAST ONE EXIT #########
    ##########################################################
    exitGate = random.choice(gates)
    playerPath = getPlayerPath(Game.player, exitGate, Game.grid,
                               wallWidth=vertWallDecor.width, wallHeight=horizWallDecor.height)

    #turn player path into hitbox path as wide and tall as player
    pathHB = set(itertools.chain( (hbY + y, hbX + x) for hbY, hbX in Game.player.graphic.hitbox for y,x in playerPath))
    entities.extend(gameEntities.gameEntity(Game.gaLibrary['debug'], y, x) for y,x in pathHB)

    return entities


#todo called when player dies,  prepeare dict with any relevant info, score, reason for dying
def getGameOverDictionary(game):
    return {}