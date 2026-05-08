savedcmd_furrow.ko := ld -r -m elf_x86_64 -z noexecstack --no-warn-rwx-segments --build-id=sha1  -T /home/lamb/opt/linux/scripts/module.lds -o furrow.ko furrow.o furrow.mod.o .module-common.o
