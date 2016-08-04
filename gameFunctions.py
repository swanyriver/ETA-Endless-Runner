import random
import gameEntities


# todo determine if character has entered new screen and update game layout
#return None if player still on same screen
#return (y,x) tuple for player on new screen
def playerLeftScreen(Game):
    return None

#todo generate random screens
def getNewGameRoom(Game):
    #####How to use gameEntities to create a new screen################
    # get 2 arrays of all deadly and non deadly graphics
    #hazards = [g for g in Game.gaLibrary.values() if g.deadly]
    #obstacles = [g for g in Game.gaLibrary.values() if not g.deadly]

    # check the height and width of a graphic
    #hazards[0].heigth
    #hazards[0].width

    # #create an entitity from a graphic
    # #an entity is just a graphic with an x,y position and helper methods
    # #there can be many entities made from the same graphic
    # badGuy =      gameEntities.gameEntity(hazards[0], y=10, x=20)
    # otherBadGuy = gameEntities.gameEntity(hazards[0], y=10, x=30)
    # badGuy = gameEntities.gameEntity(Game.gaLibrary['enemy'], y=10, x=20)
    #
    # #check the position, as well as bounding rectangle of an entity
    # y,x = badGuy.getYX()
    # top, left, bottom, right = badGuy.getBoundingRect()
    # top = badGuy.getTopBound()
    #
    # isDeadly = badGuy.isDeadly()

    # height, width, positions, bounding rectangles, deadly/not-deadly should be sufficient
    # to create a scheme for programaticly/psuedo-randomly/noise generate a room of objects


    #todo replace this random gen code with real code
    ###################################################################
    gaLibrary = Game.gaLibrary
    NUM_GEN = 4
    entities = []
    for k in [random.choice(gaLibrary.keys()) for _ in range(NUM_GEN)]:
        y, x = random.randint(0, 20 - 2), random.randint(0, 80 - 1)
        entities.append(gameEntities.gameEntity(gaLibrary[k], y, x))
    print entities
    return entities
    ###################################################################


#todo called when player dies,  prepeare dict with any relevant info, score, reason for dying
def getGameOverDictionary(game):
    return {}
