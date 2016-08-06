#!/bin/bash
python multithreadedserver.py -s 1>/dev/null 2>/dev/null &
PID=$!
python client.py 127.0.0.1 9999 2>/dev/null; 
kill $PID;

