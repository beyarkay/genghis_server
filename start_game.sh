#!/bin/sh
echo "--== Starting game at $1 ==--"
cd games/$1
python3 judge.py
echo "--== Ending game at $1 ==--"
cd ../