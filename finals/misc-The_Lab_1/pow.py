#!/usr/local/bin/python

import os
import sys

SECRET = "111754"

print("Enter combination:", flush=True)

guess = sys.stdin.readline().strip()

if guess == SECRET:
    with open("flag.txt") as f:
        print(f.read().strip())
else:
    print("Wrong!")
    sys.exit(1)