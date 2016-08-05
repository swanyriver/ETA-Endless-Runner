import random
import gameEntities


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
VERTWALLMAXWIDTH = 5
HORIZWALLMAXHEIGHT = 4

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
        while yend-ystart-1 > player.getHeight():
            if random.choice(["up","down"]) == "up":
                output.append(gameEntities.gameEntity(asset, ystart, xpos))
                ystart += asset.height
            else:
                yend -= asset.height
                output.append(gameEntities.gameEntity(asset, yend, xpos))

        gates.append((ystart,xpos))
        return output


def getHorizWall(asset, ypos, xstart, xend, withGate=False, withPlayer=False, player=None, gates=None):
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
        while xend - xstart - 1 > player.getWidth():
            if random.choice(["left", "right"]) == "left":
                output.append(gameEntities.gameEntity(asset, ypos, xstart))
                xstart += asset.width
            else:
                xend -= asset.width
                output.append(gameEntities.gameEntity(asset, ypos, xend))

        gates.append((xstart, ypos))
        return output


def getNewGameRoom(Game):
    """
    :type Game: game_state.Gamestate
    :return:
    """

    decor = Game.gaLibrary.getAllDecorations()
    enimies = Game.gaLibrary.getAllBadGuys()

    vertWallDecor = random.choice([d for d in decor if d.width <= VERTWALLMAXWIDTH])
    horizWallDecor = random.choice([d for d in decor if d.height <= HORIZWALLMAXHEIGHT])

    entities = []

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
                                gates=gates))
    #south
    entities.extend(getHorizWall(horizWallDecor, Game.grid.height - horizWallDecor.height, 0, Game.grid.width,
                                 withGate=SOUTH in sidesWithGates, withPlayer=SOUTH == playersSide, player=Game.player,
                                 gates=gates))

    return entities


#todo called when player dies,  prepeare dict with any relevant info, score, reason for dying
def getGameOverDictionary(game):
    return {}