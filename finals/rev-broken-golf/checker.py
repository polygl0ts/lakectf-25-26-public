#!/usr/bin/env python3
import sys
# Equivalent of stdbuf -i0 -o0 -e0
sys.stdin.reconfigure(line_buffering=True)
sys.stdout.reconfigure(line_buffering=True, write_through=True)
sys.stderr.reconfigure(line_buffering=True, write_through=True)
import base64
import os
import subprocess
import random
import resource
import ctypes
import tempfile

def preexec():
    resource.setrlimit(resource.RLIMIT_NOFILE, (0, 0))
    try: ctypes.CDLL("libc.so.6").prctl(4, 0, 0, 0, 0)
    except Exception: pass

def get_expected(args):
    ebx = 1
    for arg in args:
        ebx = (ebx * 2 if arg == "32" else ebx + 2) & 0xffffffff
    return ebx & 0xff

try: ctypes.CDLL("libc.so.6").prctl(4, 0, 0, 0, 0)
except Exception: pass

with open("chal", "rb") as f:
    challenge_data = f.read()

stripped_data = challenge_data[24:]
print(base64.b64encode(stripped_data).decode())
sys.stdout.flush()

decoded = base64.b64decode(sys.stdin.readline().strip())
print("Received data length:", len(decoded))

if len(decoded) != 24:
    print("Expected 24 bytes")
    sys.exit(1)

if decoded[4] != 2:
    print("Expected 64-bit executable")
    sys.exit(1)

elf_path = "/tmp/final_chal"

with open(elf_path, "wb") as f:
    f.write(decoded + stripped_data)

os.chmod(elf_path, 0o755)

for _ in range(100):
    args = [random.choice(["32", "64"]) for _ in range(random.randint(1, 30))]
    res = subprocess.run(
        [elf_path] + args,
        env={},
        timeout=2,
        # stdout=subprocess.DEVNULL,
        # stderr=subprocess.DEVNULL,
        preexec_fn=preexec
    )
    if res.returncode != get_expected(args):
        print("Testcase failed")
        sys.exit(1)

print(f"All tests passed! Flag: {os.environ.get('FLAG', 'flag{default_flag}')}")
