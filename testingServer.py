class gameEntity():
    def __init__(self, height, width, y, x, maxY, maxX):
        self.width = width
        self.height = height
        self.y = y
        self.x = x
        self.maxX = maxX
        self.maxY = maxY

    def move(self, ydelta, xdelta):
        if 0 <= self.x + xdelta < self.maxX - self.width:
            self.x += xdelta
        if 0 <= self.y + ydelta < self.maxY - self.height:
            self.y += ydelta

    def getpos(self):
        return self.y, self.x

directional_change = {
    "left":(0,-1),
    "right":(0,1),
    "up":(-1,0),
    "down":(1,0)
}


def gameServer(maxy, maxx, recpipe, sendpipe):

    #todo hardcoded for this test, need server side model to import same widths and heights
    character = gameEntity(4, 5, maxy//2, maxx//2, maxy, maxx)

    while 1:
        if recpipe.poll(.2):
            action=recpipe.recv()
            #todo temp protocol, later need to specify json format
            if action == "quit": return
            character.move(*directional_change.get(action, (0,0)))

        #todo need to send as json instead
        sendpipe.send(character.getpos())





# import random
#
# SPAWN_MIN_TIME = 2
# SPAWN_MAX_TIME = 15
# SPAWN_MIN = 1
# SPAWN_MAX = 5
#
# #todo function,  tuple from json
# directional_change = {
#     ACTIONS.left:(0,-1),
#     ACTIONS.right:(0,1),
#     ACTIONS.up:(-1,0),
#     ACTIONS.down:(1,0)
# }
#
# class Character():
#     def __init__(self, y, x):
#         self.x = x
#         self.y = y
#         self.width = 5
#         self.height = 4
#
#     def getDrawing(self):
#         return ["  *  ",
#                 " <*> ",
#                 "<***>",
#                 " ^ ^ "]
#
#
#
# class Speck():
#     def __init__(self, ymax, xmax):
#
#         self.ymax = ymax
#         self.xmax = xmax
#
#         self.xdelta = random.choice(range(-6,0) + range(1, 6))
#         self.ydelta = random.choice(range(-6,0) + range(1, 6))
#
#         if random.choice((True, False)):
#             # put on side walls
#             self.x = 0 if self.xdelta > 0 else xmax
#             self.y = random.randint(0, ymax)
#         else:
#             self.y = 0 if self.ydelta > 0 else ymax
#             self.x = random.randint(0, xmax)
#
#         self.inbounds = True
#
#     def move(self):
#         self.x += self.xdelta
#         self.y += self.ydelta
#         self.inbounds = 0 <= self.x <= self.xmax and 0 <= self.y <= self.ymax
#
#
# #todo the game x/y bounds and the render x/y bounds must be kept seperate
# #todo respond to user resize events (getch KEY_RESIZE) (or just beg the prof not to resize in the middle of a game) in view controler
# #todo at the very least ensure that drawing out of bounds does not crash the game
# class Game():
#     def __init__(self, height, width):
#         self.character = Character(height // 2, width // 2)
#         self.maxX = width
#
#         # this is a hack for now, to solve a problem with curses difficulty writing a character in the very bottom right
#         # http://stackoverflow.com/questions/36387625/curses-calling-addch-on-the-bottom-right-corner
#         self.maxY = height - 1
#         self.noise = []
#         self.nextNoiseTick = 0
#
#     def getCharPos(self):
#         return self.character.y, self.character.x
#
#     #this is a request from the controller, not an imitative, game model will determine if move is possible

#
#     def tick(self):
#         for speck in self.noise:
#             speck.move()
#         self.noise = [sp for sp in self.noise if sp.inbounds]
#
#         if self.nextNoiseTick <= 0:
#             self.nextNoiseTick = random.randint(SPAWN_MIN_TIME, SPAWN_MAX_TIME)
#             for _ in range(random.randint(SPAWN_MIN, SPAWN_MAX)):
#                 self.noise.append(Speck(self.maxY-1, self.maxX-1))
#
#         self.nextNoiseTick -= 1
#
#     def getNoise(self):
#         return [(sp.y, sp.x) for sp in self.noise]
#
#     def getCharacterDrawing(self):
#         return self.character.getDrawing()
