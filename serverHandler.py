#!/usr/bin/python2.7

def printError(string):
    #select client who sent message last and have the server return the error string
    server.send(string)

def serverHandler(charInput):
    if charInput == A: 
        movePlayerWest()
    elif charInput == W: 
        movePlayerNorth()
    elif charInput == S: 
        movePlayerSouth()
    elif charInput == D: 
        movePlayerEast
    elif charInput== /:
        sendChat()
    else:
        printError("you entered a single Character which is not a directon")#TODO make printError Function
