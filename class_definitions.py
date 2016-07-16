import time

#NOTES:
#store location (player)
#client sends awsd and server does processing
#UDP-style client coordinating

#Functions to Use:
#game = Gamestate()
#game.startTimer()
#game.stopTimer()
#game.gameTime is the total elapsed time
#             still determining score..
#game.newPlayer. movePlayerUp(playableGrid, newPlayer) syntax?
#game.newPlayer. movePlayerDown(playableGrid, newPlayer)
#game.newPlayer. movePlayerLeft(playableGrid, newPlayer)
#game.newPlayer. movePlayerRight(playableGrid, newPlayer)
#

#gamestate class
#set up gamestate and keeps track of user scores and grid
class Gamestate():
                t0, t1

                #sets up initial variables and grid
                def __init__(self):
                                newGrid = Grid()
                                roomsCrossed = 0
                                score = 0
                                gameTime = 0
                                newPlayer = Player()
 
                                #add obstacles initially?

                                #adds player to middle of grid
                                #Player._set_location(newPlayer, newGrid.midY, newGrid.midX)

                #add timer
                def startTimer(self):
                                t0 = time.time()

                #end timer
                def endTimer(self):
                                t1 = time.time()
                                gameTime = t1 – t0

                #keep track of rooms crossed

#grid class
Class Grid():
	_width = 80
        _height = 24

        #check this!
        midY = _height/2
        midX = _width/2

        temp_location = [0 for in range(2)]

        #1 for walls, 2 for obstacles, 3 for player, 0 for free space
        #returns nothing, walls are 1 space thick
        def __init__(self):
		playableGrid = [[1 for x in range(_width)] for y in range(_height)]
        	#playableGrid = [[0 for x in range(1, _width)] for y in range(1, _height)]
                #create walls
		for x in range(1, _width):
			for y in range(1, _height):
                               	playableGrid[y][x] = 0 

        #create doors
        ##

        #random generation
        ##

        #returns updated playable grid space
        def addObstable(self, y, x ):
	        playableGrid[y][x] = 2
                return playableGrid

        #returns updated playable grid space
        def removeObstable(self, obstacle, y, x):
                Obstacle._set_location(obstacle) = {-1, -1}
                playableGrid[y][x] = 0
                return playableGrid

        #returns updated playable grid space
        def addPlayer(self, player, y, x):
        	Player._set_location(player, y, x)
                playableGrid[y][x] = 3
                return playableGrid

        #returns updated playable grid space
        def removePlayer(self, player, y, x):
        	Player._set_location(player) = {-1, -1}
                playableGrid[y][x] = 0
                return playableGrid

        #move player functions, includes cleanup but
        #assumes there is going to be empty space behind the player
        def movePlayerUp(self, player):
	        temp_location = Player._get_location(player)
	        playableGrid[temp_location[0]][temp_location[1]] = 0
	        Player._move_up(player)
	        playableGrid[temp_location[0]][temp_location[1]] = 3

        def movePlayerDown(self, player):
        	temp_location = Player._get_location(player)
        	playableGrid[temp_location[0]][temp_location[1]] = 0
        	Player._move_down(player)
        	playableGrid[temp_location[0]][temp_location[1]] = 3

        def movePlayerLeft(self, player):
	        temp_location = Player._get_location(player)
	        playableGrid[temp_location[0]][temp_location[1]] = 0
	        Player._move_left(player)
	        playableGrid[temp_location[0]][temp_location[1]] = 3

        def movePlayerRight(self, player):
	        temp_location = Player._get_location(player)
	        playableGrid[temp_location[0]][temp_location[1]] = 0
	        Player._move_right(player)
	        playableGrid[temp_location[0]][temp_location[1]] = 3


#player class
class Player():
#location is set by placement of "feet" of character
    #takes up one space, variable is a coordinate array
    #shouldn't automatically be 0,0; will be changed
    def __init__(self, name):
        self.name = name
        self._col_num = 2

        #list comprehension, python's equivalent to
        # c's int location[2];
        self.location = [0 for in range(self._col_num)]

    #used to set initial player location in a map
    def _set_location(self, row, col):
        self.location[0] = row
        self.location[1] = col

    #returns current location

    def _get_location(self):
        return self.location

    #functions for single-space movement
    def _move_up(self):
        self.location[1] =  self.location[1] + 1

    def _move_down(self):
        self.location[1] = self.location[1] - 1

    def _move_left(self):
        self.location[0] = self.location[0] - 1

    def _move_right(self):
        self.location[0] - self.location[0] + 1

 

#obstacle class

Class Obstacle():

#location is set by placement of "base" of obstacle
    #takes up one space, variable is a coordinate array
    #shouldn't automatically be 0,0; will be changed
    def __init__(self, name):
        self.name = name
        self._col_num = 2

        #list comprehension, python's equivalent to
        # c's  int location[2];
        self.location = [0 for in range(self._col_num)]

    #used to set initial player location in a map
    def _set_location(self, row, col):
        self.location[0] = row
        self.location[1] = col

    #returns current location
    def _get_location(self):
        return self.location

    #functions for single-space movement

    #do obstacles need movement functions?
    def _move_up(self):
        self.location[1] =  self.location[1] + 1

    def _move_down(self):
        self.location[1] = self.location[1] - 1

    def _move_left(self):
        self.location[0] = self.location[0] - 1

    def _move_right(self):
        self.location[0] - self.location[0] + 1

 
