import time
import json
import gameEntities
import graphicAssets
import random

#######todo remove ######################################################
#Note:  for demo purposes only
def getRandomWorld(gaLibrary):
    NUM_GEN = 4
    entities = []
    availables = filter(lambda k: k != "character", gaLibrary.keys())
    for k in [random.choice(availables) for _ in range(NUM_GEN)]:
        y, x = random.randint(0, 20 - 2), random.randint(0, 80 - 1)
        entities.append(gameEntities.gameEntity(gaLibrary[k], y, x))
    return entities
##########################################################################

#player class: initializes location to outside the grid
class Player():
    #takes up one space, which shouldn't automatically be -1, -1;
    #invalid location until set for gameplay
    def __init__(self):
        #self.name = name
        self.x = -1
        self.y = -1

#	def get_location(self):
#		return y, x

    #functions for single-space movement
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

    #sends a json message to _________
    #IS THIS RIGHT??
    # def update(self):
    #     data = {'name': self.name, 'x': self.x, 'y': self.y}
    #     json.dumps(data)
    #     return

    #recieves a json message from ______
    def get_change_request(self, m):
        req = json.loads(m)
        #do something here..
        return

#obstacle class: initializes location to outside the grid
class Obstacle():
    #x,y represent top left
    #invalid location until set for gameplay
    def __init__(self, name):
        self.name = name
        self.x = -1
        self.y = -1

#	def get_location(self):
#		return y, x

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
    height = 24

    #function to set grid width and height
    def set_width(self, new_w):
        self.width = new_w
    def set_height(self, new_h):
        self.height = new_h

    #sends a json message to _________
    #IS THIS RIGHT??
    def update(self):
        data = {'width': self.width, 'height': self.height}
        json.dumps(data)
        return

    #recieves a json message from ______
    def get_change_request(self, m):
        req = json.loads(m)
        #do something here..
        return

#gamestate class: set up gamestate and keeps track of user scores
#and grid. I don't believe the Gamestate class itself stores instances
#of any other class
class Gamestate():

    #sets up initial variables and grid
    def __init__(self):
        self.grid = Grid()
        self.roomsCrossed = 0
        self.score = 0
        self.gameTime = 0
        self.player = Player()
        self.t0 = 0
        self.t1 = 0
        self.gaLibrary = graphicAssets.getAllAssets()


        #add obstacles initially?
        self.entities = getRandomWorld(self.gaLibrary)

        #adds player to middle of grid
        self.player.set_x(self.grid.width/2)
        self.player.set_y(self.grid.height/2)

    #add timer
    def startTimer(self):
        self.t0 = time.time()
    #end timer
    def endTimer(self):
        self.t1 = time.time()
        self.gameTime = (self.t1 - self.t0)

    #keep track of rooms crossed

    def get_update(self):
        return gameEntities.JSONforNetwork(screen=self.entities, charX=self.player.x, charY=self.player.y)

    #recieves a character from client
    def get_change_request(self, msg):
        # todo colision, death, boundry detection  Here or in the move functions
        if msg == "w":
            self.player._move_up()
        elif msg == "a":
            self.player._move_left()
        elif msg == "s":
            self.player._move_down()
        elif msg == "d":
            self.player._move_right()


        # todo determine if character has entered new screen and update game layout

        # todo send screen update msg if entered new room

        return gameEntities.JSONforNetwork(charX=self.player.x, charY=self.player.y)

