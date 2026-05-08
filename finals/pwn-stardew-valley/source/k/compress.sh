#!/bin/bash

# Create a dummy exploit.c if it doesn't exist
if [ ! -f exploit.c ]; then
  echo -e '#include <stdio.h>\n\nint main() {\n  printf("hello\\n");\n  return 0;\n}' > exploit.c
  echo "exploit.c didn't exist so I created it."
fi

# Compile the exploit and compress the rootfs
# Using musl so the exploit binary is smaller and easier to transfer
bear -- musl-gcc exploit.c -o exploit -lpthread -static -Wall -Wextra -Wno-unused-function -I$HOME/code/kernel-apostle/lib/
cp exploit rootfs
cp exploit rootfs/ex
cd rootfs
# The '--owner=root' part allows us to not have to run this script as root.
find . -print0 | cpio -o --null --format=newc --owner=root > ../debugfs.cpio
cd ../
