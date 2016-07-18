#!/usr/bin/python2.7

def printError(string):
    #select client who sent message last and have the server return the error string
    server.send(string)

def serverHandler(charInput,playableGrid,player):
    if charInput == "A": 
        movePlayerleft(playableGrid,player)
    elif charInput == "W": 
        movePlayerUp(playableGrid,player)
    elif charInput == "S": 
        movePlayerDown(playableGrid,player)
    elif charInput == "D": 
        movePlayerRight(playableGrid,player)
    elif charInput== "/":
        sendChat()
    elif charInput=="q"
        exit()
    else:
        printError("you entered a single Character which is not a directon")#TODO make printError Function

