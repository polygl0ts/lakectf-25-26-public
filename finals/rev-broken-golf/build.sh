#!/bin/bash

nasm -f bin -o chal chal.s && chmod +x challenge
dd if=chal of=chal_missing_24_bytes skip=24 bs=1 
head -c 24 chal | base64 | python3 checker.py
