#!/bin/sh
rm -rf unlink-this
mkdir -p unlink-this
cp unlink unlink-this
cp unlink.c unlink-this
cp Dockerfile unlink-this
cp compose.yaml unlink-this
cp Makefile unlink-this
cp run unlink-this
tar cvfz unlink-this.tar.gz unlink-this/ 
rm -rf unlink-this
