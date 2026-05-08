# Gun

+ Author: k4lizen
+ Category: pwn
+ Intended difficulty: easy/medium
+ Solves during competition: 5/10

I'll publish a more detailed writeup with my authoring experience on [my blog](https://hazyclimb.dev/) soonish.

## The challenge

There are two binaries, `rooftop` and `stairwell`. When you get connected to netcat you get connected to `rooftop`, it gives you one bitflip on the libc ELF file and spawns `stairwell` with the modified libc. Then `stairwell` gives you 8 bitflips anywhere in the address space, but only libc and ld are leaked.

## Solution

Use the 8 bitflips to modify the `initial` (used by `__run_exit_handlers`) structure to modify the `_dl_fini` pointer to point to a one gadget (the ptr is encrypted with xor + shift, but since you have bitflips it doesn't matter). Needs a smallish brute-force.

Use the libc flip to modify an instruction which makes a onegadget work, I flipped `mov ecx, 1` in the `exit` function to `mov ecx, 0`.

## Unintended

One team went with the strategy explained above, the others flipped the segment
permission bits in the libc ELF header to make the .text section/segment `rwx`.

Then they played around with using the bit flips to change the assembly of libc, usually forcing some buffer-overflow. The specifics differ significantly from team to team, so you'll have to reach out to the players to hear them, they are quite interesting. Some ideas included changing function prolog / epilog to modify the rsp push, or changing the buffer handling logic of the libc `read()` function (in both cases going for a buffer-overflow / moving the buffer).
