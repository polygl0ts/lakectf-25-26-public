tar rem :1234

add-symbol-file hackme.ko 0xffffffffc0400000

define myslab
	slab info kmalloc-256
end

define get-cache
	p ((struct slab*)({$tpage=((struct page*)vmemmap_base+($v2p($arg0)>>12)),$tpage->compound_head&1?$tpage->compound_head^1:$tpage}[1]))->slab_cache
end

define get-sheaf
	p $badshef = (unsigned long)(((struct kmem_cache*)($arg0))->cpu_sheaves)
	p $goodshef = $badshef + $gs_base
	p $goodshef
	p *(struct slub_percpu_sheaves*) $goodshef
	p *((struct slub_percpu_sheaves*) $goodshef)->main
end

# b __alloc_empty_sheaf
# b free_to_pcs

# mm/slub.c:4725 -> taken obj from arr

p $myguyloc = 0xffffffffc0201018
p $myguy = 0x1337

tb hackme.c:31
commands
	p $myguy=*((unsigned long*)$myguyloc)

	# putting this here so we don't hit is during early boot
	# allocating a sheaf that contains kmalloc-cg-512
	# b __alloc_empty_sheaf if s->name[0] == 'k' && s->name[8] == 'c' && s->name[11] == '5'

	pi gdb.execute("continue")
end

# \/ the kzalloc in __alloc_empty_sheaf
tb mm/slub.c:2773 if (unsigned long)sheaf == (unsigned long)$myguy
commands
	# get the address of sk_buff->head
	# at net/core/skbuff.c:714
	tb *0xffffffff8276ab48
	commands
		p $mybuf = $rax

		tb *0xffffffff8276ab48
		commands
			p $mybuf2 = $rax
			pi print("IS SAME (0x1 is good):")
			p $mybuf2 == $mybuf
			pi gdb.execute("continue")
		end

		pi gdb.execute("continue")
	end

	pi print("GOOD THINGS HAPPENING!")
	pi gdb.execute("continue")
end


continue
