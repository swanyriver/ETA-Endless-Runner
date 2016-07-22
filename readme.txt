ETA endless runner
Members: Megan Fanning, Miranda Weldon, Brandon Swanson
=======

To run program: 
first run server.py, this will print out the IP and port 
(we have hard coded the ip to local and the port to 9999 for testing).
Next begin the client.py ($ python client.py 127.0.0.1 9999)
once the server and the client connect the game will begin (a curses screen will open and display images).

Game play mechanics:
One player will control the vertical axis and the other player will control the horizontal axis of movement.
(for testing purposes we will only have one client connecting who will control both horizontal and vertical movement)
The player must navigate around obstacles and move to the exit of the screen to progress through the levels.

Controls:
players direct movement using wasd or arrow keys to move,  q or esc key to quit.

Networking 
The network client accepts: strings of user input and passes them to the server as either strings 
(for messages) or constants (for directions) from the curses interface.The server returns: JSON 
formatted files containing information about player location and graphics. 
Functionality: Upon accepting user input the client sends the data to the server, the server then 
parses user input for movement keys. If a movement key is found then the game state is 
updated and this update is sent back to the client. 
 
Game State 
The Player class handles single space movement. The Obstacle class places and update 
obstacles in a room. The Grid class keeps track of dimensions (width and height) of playable 
grid. The Gamestate class keeps track of timing, scoring mechanisms, sets graphical assets, 
sends requests to update other classes’ variables. All of these classes come together to keep 
track of all the internal game state variables that keep this game running consistently. 

Curses Engine 
The curses engine is launched as a separate process and manages collecting input from the 
user (non-blocking) and rendering the game state as it is transmitted from the server.  The 
curses process communicates with the network interface over a Pipe connection allowing the 
network and curses component to communicate using a producer-consumer pattern.  Rending 
game entities that share property definitions between server and client, defining ascii art in an 
external file library, and transmitting the game state from server to client “by-name” as opposed 
to “by-drawing” are all achieved through the combination of the GraphicAsset and GameEntity 
classes. 


For further documentation see: ETAMid-PointDocumentation.pdf

