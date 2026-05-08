# stardew-valley

+ Author: P.Howe & k4lizen
+ Category: pwn
+ Intended difficulty: hard
+ Solves during competition: 2/10

post-competition comment: When writing the module for this challenge I forgot to include a `stage += 1` in the `stage == 2` branch. Oops. You were intended to be able to increase the number only once. With two increases available, both teams who solved it went with Page Table Entry spray, allowing them to change the permission bits of an `/etc/passwd` mmaped page from read-only to read-writable.

I'll write a more detailed writeup on [my blog](https://hazyclimb.dev/) later.

See `./source/exploit.c` for the exploit.

## Overview

Kernel privesc challenge with a vulnerable kernel module. Kernel version v7.0-rc3 .

This is the vuln kernel module:
```c
static long furrow_ioctl(struct file* file, unsigned int cmd,
                             unsigned long arg) {
  if (stage == 0) {
    stage += 1;
    // till the dirt
    furrow_obj = (struct furrow*)kmalloc(0x100, GFP_KERNEL);
    memset((void*)furrow_obj, 'T', 0x100);
  } else if (stage == 1) {
    stage += 1;
    // oh noes a storm!
    kfree(furrow_obj);
  } else if (stage == 2) {
    // this one was under cover, needs watering still :3
    furrow_obj->bed4 += 1;
  } else {
    return -EINVAL;
  }
  return 0;
}
```

## Solution

The problem is essentially to find a useful object to overlap `furrow_obj` with (since it is under Use-After-Free), such that a `+1` on the 4th qword does something useful.

In kernel `v7.0-rcX` the `kmem_cache_cpu` struct was replaced with "sheaf" logic. The intended solve is that
you overlap `furrow_obj` with a `struct slab_sheaf`:
```c
struct slab_sheaf {
	union {
		struct list_head barn_list;
		/* only used for prefilled sheafs */
		unsigned int capacity;
	};
	struct kmem_cache *cache;
	unsigned int size;
	int node; /* only used for rcu_sheaf */
	void *objects[];
};
```
This thing is allocated on the heap and you can increase it's `size` field. The problem is consistently
getting an overlap with the sheaf, i.e. the problem is controlling when a `slab_sheaf` will get allocated.

Ideally you want to go for a low-noise cache, we went for `kmalloc-cg-512` allocated by `sk_buff->head`s. You need
to do some heap feng shui to get a consistent setup. After that, by using the UAF you falsely increase the
`size` counter. The `objects` list is a list of free slots that get taken via `kmalloc`, so by increasing the
`size` counter, you can get two different `kmalloc`'s to return the same pointer.

Then you can cross-cache into dirty-cred to get a root shell. 


