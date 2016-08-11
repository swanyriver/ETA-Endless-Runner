ETA endless runner
Members: Megan Fanning, Miranda Weldon, Brandon Swanson
=======

To run program: 
To Launch in two player mode:
Step one: Launch server using the following command supplying an optional port number or allowing the kernel to allocate an arbitrary port number:
$ python multithreadedserver.py [PORT-NUMBER]

Once launched the server will display the ip address and port number necessary for connecting to it, as well as print logging information about network traffic and from the game state

Step two: Launch 2 connected connects clients in separate connections to the same flip server.
	-$ python client.py 127.0.0.1 <PORT-NUMBER>
	-$ python client.py 127.0.0.1 <PORT-NUMBER>

To Launch in one player mode:
The provided shell script singlePlayer.sh will launch the server script in the background, with a single player flag supplied and with its logging output redirected, and then launch a connected client with full movement privileges.  Allowing you to play the game in a single terminal/flip-connection.

Launch in command line use:
     $ ./singlePlayer.sh <PORT-NUMBER> or
     $ bash singlePlayer.sh <PORT-NUMBER>
A valid port number must be supplied as the first and only command line argument in this case to allow the client to automatically connect to the initiated server.


Game play mechanics:
One player will control the vertical axis and the other player will control the horizontal axis of movement.

The players must navigate around obstacles and move to the exit of the screen to progress through the levels.

Controls:
players direct movement using wasd or arrow keys to move.
pressing "/" will allow you to enter a chat message to the other player (enter to send, delete or ESC to cancel)
pressing "q" or ESC will quit the game and disconnect from the server,  but game will still be running waiting for you
or another player to rejoin your partner and finish the game.

Networking:
Accepts: strings of user input and passes them to the server as either strings (for messages) or constants (for directions)
Returns: JSON formatted files containing information about player location and graphics.
