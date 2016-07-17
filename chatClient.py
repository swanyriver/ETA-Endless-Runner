#!/usr/bin/python2.7

#Megan Fanning
#Project: Create a chat Client
#chatclient starts on host B, 
# accepts hostname/ip as first argument and tcp port as second arguement
# references
# https://wiki.python.org/moin/TcpCommunication 
import sys
import socket

#get the user's "handle" by initial query
# handle is a one-word name, up to 10 characters. 
def getUsersHandle():
    print("What would you like to your handle, it must be 10 characters or less")

    person = raw_input('Enter your name: ')
    #check if handle is less than 10 char 
    if(len(person) > 10):
        print("error! requested handle is too long")
        person=getUsersHandle();

    #check if there are spaces in handle
    if(" " in person): 
        print("There's a space in your username")
        person=getUsersHandle();
    return person

def sendMsg(input,usersHandle):
    #prepend users handle and append newline
    return usersHandle+">"+input+"\n" 

#should be able to get hostname, messages etc    
def getUserInput(user):
    userInput = raw_input(user+'>')
    return userInput

def main():
    #specify host A's hostname and port number on the command line.
    TCP_IP = "localhost" #sys.argv[1]
    TCP_PORT = 9999 #int(sys.argv[2])  
    BUFFER_SIZE = 1024
    quit="\quit"

    #create sock stream and connect  
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))

    #get user Handle
    userHandle = getUsersHandle()
    #get initial input
    msg = getUserInput(userHandle)
    MESSAGE = sendMsg(msg,userHandle)

    #while the user hasn't quit send and receive msgs
    while(msg != quit):
        #send message
        s.send(MESSAGE.encode())
        data = s.recv(BUFFER_SIZE).decode()
        sys.stdout.write(data)

        #get user MSG
        msg = getUserInput(userHandle)
        MESSAGE = sendMsg(msg,userHandle)
    #close connection
    s.close()

if __name__ == "__main__":
    main()#TODO add back argv to allow random ports
