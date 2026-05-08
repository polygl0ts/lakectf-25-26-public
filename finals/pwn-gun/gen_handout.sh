#!/bin/sh

rm -rf handout
mkdir -p handout
cp source/Makefile handout/.
cp source/rooftop handout/.
cp source/rooftop.c handout/.
cp source/ascii_art.h handout/.
cp source/stairwell handout/.
cp source/stairwell.c handout/.
cp source/run handout/.
cp source/libc.so.6 handout/.
cp source/ld-linux-x86-64.so.2 handout/.

cp ./compose.yaml handout/.
cp ./Dockerfile handout/.

echo "EPFL{fake-flag}" > handout/flag.txt

tar cvfz gun.tar.gz handout/ 
rm -rf handout/
