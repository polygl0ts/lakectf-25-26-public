v7.0-rc3

REPOSITORY_URL=https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
TAG=v7.0-rc3
COMMIT_HASH=1f318b96cc84d7c2ab792fcc0bfd42a7ca890681

```bash
HERE=$PWD

cd ~/opt/linux
git checkout v7.0-rc3

make mrproper
wget https://storage.googleapis.com/kernelctf-build/releases/lts-6.12.74/.config -O .config

./scripts/config --set-val CONFIG_DEBUG_INFO y
./scripts/config --set-val CONFIG_DEBUG_INFO_DWARF5 y
./scripts/config --set-val CONFIG_GDB_SCRIPTS y
./scripts/config --set-val CONFIG_DEBUG_KERNEL y
./scripts/config --set-val CONFIG_FRAME_POINTER y

make olddefconfig
cp .config $HERE/kconfig

make -j $(nproc) HOSTCC=gcc-11 CC=gcc-11 KCFLAGS="-Wno-error"
./scripts/clang-tools/gen_compile_commands.py

cd $HERE

cp ~/opt/linux/arch/x86/boot/bzImage .
cp ~/opt/linux/vmlinux .
```
