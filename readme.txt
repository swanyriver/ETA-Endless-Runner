ETA endless runner
Members: Megan Miranda Brandon
=======

To run program: 
first run server.py, this will print out the IP and port (we have hard coded the ip to local and the port to 9999 for testing).
Next begin the client.py ($ python client.py 127.0.0.1 9999)
once the server and the client connect the game will begin (a curses screen will open and display images).

Game play mechanics:

Networking:
Accepts: strings of user input and passes them to the server as either strings (for messages) or constants (for directions)
Returns: JSON formated files containing information about player location and graphics


Game Image:

Game State:
