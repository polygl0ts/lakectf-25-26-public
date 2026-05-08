#!/usr/bin/env python3
from pwn import *

context.log_level = "debug"

PRISONER_SCRIPT = b"""import sys
for e,line in enumerate(sys.stdin):
    if e == 0: print(line.split("number ")[1].split(".")[0].strip())
    elif line.startswith("FOUND "):
        print(int(line.split()[1]))
EOF
"""

# check that we cannot dump the environment lol
# PRISONER_SCRIPT = b"""
# import os
# os.system("base64 -w0 /proc/5/environ")
# EOF
# """

# io = process("FLAG=ciao ./chal -v", shell=True)
io = remote("localhost", 6667)
# io = remote("chall.polygl0ts.ch", 6667)
for p in range(1, 101):
    io.recvuntil(b"EOF' on its own line):\n")
    io.send(PRISONER_SCRIPT)
    got = io.recvuntil((f"Player {p} succeeded.\n".encode(),
                        f"Player {p} failed".encode()), timeout=3)
    if b"failed" in got:
        io.close()
        print("Player", p, "failed")
        exit(1)
flag = io.recvall(timeout=1).decode(errors="ignore")
print(flag)
