#NOTES:
#store location (player)
#	client sends awsd and server does processing
#send json of player and obstacle(s) locations, (y,x)
#UDP-style client coordinating

#player class
#main question: are we wanting to return an int for any movement function or for set?
class Player():
	#location is set by placement of "feet" of character
	#takes up one space, variable is a coordinate array
	#shouldn't automatically be 0,0; will be changed
	def __init__(self, name):
		self.name = name
		self._col_num = 2

		#list comprehension, python's equivalent to
		# c's self.location = {0,0}
		self.location = [0 for in range(self._col_num)]

	#used to set initial player location in a map
	def _set_location(self, row, col):
		self.location[0] = row
		self.location[1] = col
		return self.location

	#i'm nervous about messing with location directly, use this
	def _get_location(self):
		return self.location

	#functions for single-space movement
	def _move_up(self):
		self.location[1]++
		return location
	def _move_down(self):
		self.location[1]--
		return location
	def _move_left(self):
		self.location[0]--
		return location
	def _move_right(self):
		self.location[0]++
		return location
