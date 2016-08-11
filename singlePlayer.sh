#!/bin/bash

#stop other instances of our game servers from running on that port
#waits for port to be freed but only if port was in use
fuser ${1}/tcp -k > /dev/null 2>&1 && sleep .5

#Launch server with supplied port and flag for single player mode
#Launch in background and redirect output, allowing curses to run in same terminal
python multithreadedserver.py $1 -s 1>/dev/null 2>/dev/null &
PID=$!

#launch connected client
python client.py 127.0.0.1 $1 2>/dev/null;

#Terminate single use server 
kill $PID > /dev/null 2>&1;

