#!/bin/bash
python multithreadedserver.py $1 -s 1>/dev/null 2>/dev/null &
PID=$!
python client.py 127.0.0.1 $1 2>/dev/null; 
kill $PID;

