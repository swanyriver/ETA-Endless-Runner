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
    hazards = [g for g in Game.gaLibrary.values() if g.deadly]
    obstacles = [g for g in Game.gaLibrary.values() if not g.deadly]

    # check the height and width of a graphic
    #hazards[0].heigth
    #hazards[0].width
    
    #create entities from graphics, three hazards but no obstacles
    #an entity is just a graphic with an x,y position and helper methods
    #there can be many entities made from the same graphic
    #20 and 80 are the default height and width of the playable grid, can be changed to new grid size if appliacable
    randNum = random.choice(gaLibrary.keys()) for _ in range(4)
    y, x = random.randint(0, 20 - 2), random.randint(0, 80 - 1)
    badGuy = gameEntities.gameEntity(hazards[randNum], y, x)
    randNum = random.choice(gaLibrary.keys()) for _ in range(4)
    y, x = random.randint(0, 20 - 2), random.randint(0, 80 - 1)
    otherBadGuy = gameEntities.gameEntity(hazards[randNum], y, x)
    randNum = random.choice(gaLibrary.keys()) for _ in range(4)
    y, x = random.randint(0, 20 - 2), random.randint(0, 80 - 1)
    yetAnotherBadGuy = gameEntities.gameEntity(hazards[randNum], y, x)
    
    #what is this doing that's different from before?
    #badGuy = gameEntities.gameEntity(Game.gaLibrary['enemy'], y=10, x=20)
    
    # #check the position, as well as bounding rectangle of an entity
    # y,x = badGuy.getYX()

    top, left, bottom, right = badGuy.getBoundingRect()
    oTop, oLeft, oBottom, oRight = otherBadGuy.getBoundingRect()
    yTop, yLeft, oBottom, yRight = yetAnotherBadGuy.getBoundingRect()

    #if any numbers in range overlap, then entities overlap on screen
    #WARNING: moves characters only right and down, may force offscreen

    #compare badGuy and otherBadGuy
    if range(max(right, oRight), min(left, oLeft))
        for #count numbers in prev range, called diff
            otherBadGuy.setYX(oLeft, oRight + diff)
    if range(max(top, oTop), min(bottom, oBottom))
        for #count numbers in prev range, called diff
            otherBadGuy.setYX(oTop, oBottom + diff)
    #compare otherbadGuy and yetAnotherBadGuy
    if range(max(oRight, yRight), min(oLeft, yLeft))
        for #count numbers in prev range, called diff
            yetAnotherBadGuy.setYX(yLeft, yRight + diff)
    if range(max(oTop, yTop), min(oBottom, yBottom))
        for #count numbers in prev range, called diff
            yetAnotherBadGuy.setYX(yTop, yBottom + diff)
    #compare badGuy and yetAnotherBadGuy
    if range(max(right, yRight), min(left, yLeft))
        for #count numbers in prev range, called diff
            badGuy.setYX(left, right + diff)
    if range(max(oTop, yTop), min(oBottom, yBottom))
        for #count numbers in prev range, called diff
            yetAnotherBadGuy.setYX(top, bottom + diff)

    # top = badGuy.getTopBound()
    #
    # isDeadly = badGuy.isDeadly()

    # height, width, positions, bounding rectangles, deadly/not-deadly should be sufficient
    # to create a scheme for programaticly/psuedo-randomly/noise generate a room of objects

    print badGuy, otherBadGuy, yetAnotherBadGuy
    return badGuy, otherBadGuy, yetAnotherBadGuy

#    #todo replace this random gen code with real code
#    ###################################################################
#    gaLibrary = Game.gaLibrary
#    NUM_GEN = 4
#    entities = []
#    for k in [random.choice(gaLibrary.keys()) for _ in range(NUM_GEN)]:
#        y, x = random.randint(0, 20 - 2), random.randint(0, 80 - 1)
#        entities.append(gameEntities.gameEntity(gaLibrary[k], y, x))
#    print entities
#    return entities
#    ###################################################################


#todo called when player dies,  prepeare dict with any relevant info, score, reason for dying
def getGameOverDictionary(game):
    return {}
