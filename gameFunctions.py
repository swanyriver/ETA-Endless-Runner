import random
import gameEntities
import itertools
from log import log
import graphicAssets
from networkKeys import *

#return False if player still on same screen
#update player position and score if changed screen
def playerLeftScreen(Game):
    halfW = Game.player.getWidth()//2
    halfH = Game.player.getHeight()//2
    if Game.player.y < -halfH:
        Game.roomsCrossed += 1
        Game.player.set_y(Game.grid.height - halfH - 1)
        return True
    elif Game.player.y > Game.grid.height - halfH:
        Game.roomsCrossed += 1
        Game.player.set_y(-halfH)
        return True
    elif Game.player.x < -halfW:
        Game.roomsCrossed += 1
        Game.player.set_x(Game.grid.width - halfW - 1)
        return True
    elif Game.player.x > Game.grid.width - halfW:
        Game.roomsCrossed += 1
        Game.player.set_x(-halfW)
        return True
    else:
        return False


NORTH = 0
SOUTH = 1
EAST = 2
WEST = 3
SIDES = [NORTH, SOUTH, EAST, WEST]
SIDENAMES = {NORTH:"NORTH", SOUTH:"SOUTH", EAST:"EAST", WEST:"WEST"}
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

    log("(GAME-GEN) player on: %s (%d,%d)  exit on: %s (%d,%d)\n"%(SIDENAMES.get(playerSide,None), playerY, playerX,
                                                                   SIDENAMES.get(exitSide, None), exitY, exitX))

    path = []
    #reserve space through entrance
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

    #Generate path from opposite walls
    if sorted([playerSide, exitSide]) == sorted([NORTH, SOUTH]):
        genInnerPath = random.choice((True, False))
        if genInnerPath:
            pivotPoint = random.randint(wallHeight, grid.height - wallHeight - player.getHeight())
            path.extend( (y, playerX) for y in inclusiveRange(playerY, pivotPoint) )
            path.extend( (pivotPoint, x) for x in inclusiveRange(playerX, exitX) )
            path.extend( (y, exitX) for y in inclusiveRange(pivotPoint, exitY))
        else:
            #outer path to opposite gate
            #go left or right
            if random.choice("lr") == "l":
                vertPathX = wallWidth
            else:
                vertPathX = grid.width - wallWidth - player.getWidth()

            path.extend( (playerY, x) for x in inclusiveRange(playerX, vertPathX))
            path.extend( (y, vertPathX) for y in inclusiveRange(playerY, exitY))
            path.extend( (exitY, x) for x in inclusiveRange(vertPathX, exitX))

    elif sorted([playerSide, exitSide]) == sorted([EAST, WEST]):
        genInnerPath = random.choice((True, False))
        if genInnerPath:
            pivotXPoint = random.randint(wallWidth, grid.width - wallWidth - player.getWidth())
            path.extend( (playerY, x) for x in inclusiveRange(playerX, pivotXPoint))
            path.extend( (y, pivotXPoint) for y in inclusiveRange(playerY, exitY))
            path.extend( (exitY, x) for x in inclusiveRange(pivotXPoint, exitX))
        else:
            #randomly up or down
            if random.choice("ud") == "u":
                horizPathY = wallHeight
            else:
                horizPathY = grid.height - wallHeight - player.getHeight()

            path.extend((y, playerX) for y in inclusiveRange(playerY, horizPathY))
            path.extend((horizPathY, x) for x in inclusiveRange(playerX, exitX))
            path.extend((y, exitX) for y in inclusiveRange(horizPathY, exitY))

    # Generate cornered path
    else:
        vertFirst = random.choice((True,False))
        if vertFirst:
            path.extend( (y, playerX) for y in inclusiveRange(playerY, exitY))
            path.extend( (exitY, x) for x in inclusiveRange(playerX, exitX))
        else:
            path.extend( (playerY, x) for x in inclusiveRange(playerX, exitX))
            path.extend( (y, exitX) for y in inclusiveRange(playerY, exitY))

    return path


def deltaHB(hb, y, x):
    return [(hbY + y, hbX + x) for hbY,hbX in hb]


def getNewGameRoom(Game):
    """
    :type Game: game_state.Gamestate
    :return:
    """

    category = random.choice(Game.gaLibrary.getCategories())
    log("(GAME-GEN): category for new room is: %s\n"%category)
    decor = Game.gaLibrary.getDecorations(category)
    entities = []


    #############################
    #### CREATE WALLS & GATES ###
    #############################
    vertWallDecor = random.choice([d for d in decor if d.width <= graphicAssets.VERTWALLMAXWIDTH])
    horizWallDecor = random.choice([d for d in decor if d.height <= graphicAssets.HORIZWALLMAXHEIGHT])
    playersSide = playerOnSide(Game.player, Game.grid)
    sidesWithGates = random.sample([side for side in SIDES if side != playersSide], random.randint(1, 3))

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


    ##############################
    ### BLOCK PLAYER RETREAT #####
    ##############################
    if playersSide == NORTH:
        entities.append(gameEntities.gameEntity(Game.horizBlocker, Game.player.y-1, 0))
    elif playersSide == SOUTH:
        entities.append(gameEntities.gameEntity(Game.horizBlocker, Game.player.y + Game.player.getHeight(), 0))
    elif playersSide == WEST:
        entities.append(gameEntities.gameEntity(Game.vertBlocker, 0, Game.player.x -1))
    elif playersSide == EAST:
        entities.append(gameEntities.gameEntity(Game.vertBlocker, 0, Game.player.x + Game.player.getWidth()))


    ##########################################################
    ## RESERVE PATH FROM PLAYER TO AT LEAST ONE EXIT #########
    ##########################################################
    exitGate = random.choice(gates)
    playerPath = getPlayerPath(Game.player, exitGate, Game.grid,
                               wallWidth=vertWallDecor.width, wallHeight=horizWallDecor.height)

    #turn player path into hitbox path as wide and tall as player
    pathHB = set(itertools.chain(*(deltaHB(Game.player.graphic.hitbox, y, x) for y, x in playerPath)))

    #### DEBUG ONLY used during debug to visualize reserved path
    #entities.extend(gameEntities.gameEntity(Game.gaLibrary['debug'], y, x) for y,x in pathHB)
    ###############################################################

    ##########################################################
    #### INSERT ENIMIES AVOIDING COLISIONS AND PLAYER PATH ###
    ##########################################################
    log(str(dir(Game)) + "\n")

    enimiesToPlace = Game.numBadGuysToPlace
    enimies = Game.gaLibrary.getBadGuys(category)
    avoidHitBoxMap = set(itertools.chain(*(e.getDeltaHitbox() for e in entities)))
    avoidHitBoxMap.update(pathHB)
    negativeSpace = set((y,x)
                        for y in range(Game.grid.height)
                        for x in range(Game.grid.width)).difference(avoidHitBoxMap)

    #place enimies while we have yet to place enough and any of our enimies will fit in the remaining space
    while enimiesToPlace and enimies:
        nextEnemy = random.choice(enimies)
        availablePlacements = [ (y,x) for y,x in negativeSpace
                                if y + nextEnemy.height < Game.grid.height and
                                x + nextEnemy.width < Game.grid.width and
                                not avoidHitBoxMap.intersection(deltaHB(nextEnemy.hitbox, y,x))]
        if not availablePlacements:
            enimies.remove(nextEnemy)
        else:
            nextEnemyEntity = gameEntities.gameEntity(nextEnemy, *random.choice(availablePlacements))
            entities.append(nextEnemyEntity)
            avoidHitBoxMap.update(nextEnemyEntity.getDeltaHitbox())
            enimiesToPlace -= 1

    return entities


def getGameOverDictionary(game, killer):
    """
    :type game: game_state.Gamestate
    :type killer: gameEntities.gameEntity
    :return:
    """
    return {
        GAMEOVER.kKiller: killer.graphic.name,
        GAMEOVER.kScore: game.roomsCrossed
    }
