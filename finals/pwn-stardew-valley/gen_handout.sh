#!/bin/sh

rm -rf handout
mkdir -p handout
cp source/rootfs.cpio handout/.
cp source/furrow.c handout/.
cp source/run.sh handout/.
cp source/bzImage handout/.
cp source/BUILDING.md handout/.
cp source/Makefile handout/.
cp source/run.sh.deploy handout/run.sh

cp ./compose.yaml handout/.
cp ./Dockerfile handout/.

tar cvfz stardew-valley.tar.gz handout/ 
rm -rf handout/
