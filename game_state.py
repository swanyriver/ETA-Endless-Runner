import time
import json
import gameEntities
import graphicAssets
import gameFunctions
from networkKeys import *

#player class: initializes location to outside the grid
#player class is now a subclass of gameEntity and inherits the following properties/methods
#  x
#  y
#  graphic (reference to graphic asset instance)
#
class Player(gameEntities.gameEntity):
    #takes up one space, which shouldn't automatically be -1, -1;
    #invalid location until set for gameplay
    def __init__(self, graphicAsset=graphicAssets.getPlayerAsset()):
        super(Player, self).__init__(graphicAsset, -1, -1)


    #functions for single-space movement
    # NOTE: if these functions are ever modified to do more than set y or x
    #       then Game get_change_request() will need to be updated
    def _move_up(self):
        self.y = self.y - 1
    def _move_down(self):
        self.y = self.y + 1
    def _move_left(self):
        self.x = self.x - 1
    def _move_right(self):
        self.x = self.x + 1

    #functions to set initial player location in room
    def set_x(self, new_x):
        self.x = new_x
    def set_y(self, new_y):
        self.y = new_y

    #function to remove player from board (if needed)
    #doesn't actually get rid of object but moves player
    #outside of grid, makes player unusable
    def remove_player(self):
        self.x = -1
        self.y = -1


#obstacle class: initializes location to outside the grid
class Obstacle():
    #x,y represent top left
    #invalid location until set for gameplay
    def __init__(self, name):
        self.name = name
        self.x = -1
        self.y = -1

    #functions to set initial obstacle location in room
    def set_x(self, new_x):
        self.x = new_x
    def set_y(self, new_y):
        self.y = new_y

    #function to remove obstacle from board (if needed)
    #doesn't actually get rid of object but moves obstacle
    #outside of grid, makes it unusable
    def remove_obstacle(self):
        self.x = -1
        self.y = -1

    #sends a json message to _________
    #IS THIS RIGHT??
    def update(self):
        data = {'name': self.name, 'x': self.x, 'y': self.y}
        json.dumps(data)
        return

    #recieves a json message from ______
    def get_change_request(self, m):
        req = json.loads(m)
        #do something here..
        return

#grid class
class Grid():
    #initilized to default values for screen size
    #definitely can be changed with no apparent issue
    width = 80
    height = 20

    #function to set grid width and height
    def set_width(self, new_w):
        self.width = new_w
    def set_height(self, new_h):
        self.height = new_h


#gamestate class: set up gamestate and keeps track of user scores
class Gamestate():
    STARTING_ENEMY_AMOUNT = 2
    INCREASE_ENEMY_FREQUENCY = 4
    SCORES_TO_STORE = 10
    SCORE_FILENAME = "scores.json"

    #sets up initial variables and grid
    def __init__(self):
        self.grid = Grid()
        self.roomsCrossed = 0
        self.score = 0
        self.gameTime = 0
        self.t0 = 0
        self.t1 = 0
        self.gaLibrary = graphicAssets.getAllAssets()

        self.player = Player()

        self.isDead = False

        #used to block exit from entry door
        self.horizBlocker = graphicAssets.getHorizBlocker()
        self.vertBlocker = graphicAssets.getVertBlocker()

        # adds player to middle of grid
        self.player.set_x(self.grid.width / 2)
        self.player.set_y(self.grid.height / 2)
        self.numBadGuysToPlace = Gamestate.STARTING_ENEMY_AMOUNT
        self.countDownToExtraBadGuy = Gamestate.INCREASE_ENEMY_FREQUENCY

        self.userNames = []

        #add obstacles initially?
        self.entities = gameFunctions.getNewGameRoom(self)


    def getScoresFromFile(self):
        try:
            return json.load(open(Gamestate.SCORE_FILENAME))
        except:
            return []

    def updateScore(self, loadedScores, killerName):
        newScore = {
            SCORES.kScore: self.roomsCrossed,
            SCORES.kNames: " & ".join(self.userNames),
            SCORES.kCauseOfDeath: killerName
        }

        loadedScores.append(newScore)
        loadedScores.sort(key=lambda x:x.get(SCORES.kScore, 0), reverse=True)

        return loadedScores[:Gamestate.SCORES_TO_STORE]

    def saveScores(self, scores):
        with open(Gamestate.SCORE_FILENAME, "w") as scoreFile:
            scoreFile.write(json.dumps(scores, indent=2) + "\n")
            scoreFile.close()


    #add timer
    def startTimer(self):
        self.t0 = time.time()
    #end timer
    def endTimer(self):
        self.t1 = time.time()
        self.gameTime = (self.t1 - self.t0)


    # called once at beginning of game to create first game rendering
    # thenceforth called by game state after each player move and result returned to Network out
    def get_update(self):
        return gameEntities.JSONforNetwork(screen=self.entities, charX=self.player.x, charY=self.player.y)

    #recieves a character from client
    def get_change_request(self, msg):

        cachedPlayerPos = self.player.getYX()

        if msg == "w":
            self.player._move_up()
        elif msg == "a":
            self.player._move_left()
        elif msg == "s":
            self.player._move_down()
        elif msg == "d":
            self.player._move_right()

        playerCollision, collidedEntity = gameEntities.checkCollision(self.entities, self.player)
        if playerCollision == gameEntities.COLLIDED:
            self.player.setYX(*cachedPlayerPos)
            print "(GAME-STATE): player has collided at pos:", self.player.getYX(), "with", collidedEntity
        elif playerCollision == gameEntities.DEAD:
            print "(GAME-STATE): player has died at pos:", self.player.getYX(), collidedEntity

            print "USER NAMES:",  self.userNames

            #retrieve scores
            scores = self.getScoresFromFile()
            #update scores
            updatedScores = self.updateScore(scores, collidedEntity.graphic.name)
            #save scores
            self.saveScores(updatedScores)

            self.isDead = True

            #transmit scores
            return gameEntities.JSONforNetwork(
                charX=self.player.x,
                charY=self.player.y,
                screen=[collidedEntity],
                gameOver=gameFunctions.getGameOverDictionary(self, collidedEntity, updatedScores))


        # else: player has not collided, transmit updated position

        playerEnteredNewRoom = gameFunctions.playerLeftScreen(self)
        if playerEnteredNewRoom:

            self.countDownToExtraBadGuy -= 1
            if self.countDownToExtraBadGuy <= 0:
                self.numBadGuysToPlace += 1
                self.countDownToExtraBadGuy = Gamestate.INCREASE_ENEMY_FREQUENCY

            self.entities = gameFunctions.getNewGameRoom(self)
            return gameEntities.JSONforNetwork(screen=self.entities, charX=self.player.x, charY=self.player.y)

        else:
            return gameEntities.JSONforNetwork(charX=self.player.x, charY=self.player.y)

    def addUserName(self, name):
        self.userNames.append(name)

