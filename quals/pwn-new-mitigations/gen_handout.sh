#!/bin/sh
rm -rf new-mitigations
mkdir -p new-mitigations
cp chal new-mitigations
cp libc.so.6 new-mitigations
cp ld-linux-x86-64.so.2 new-mitigations
cp Dockerfile new-mitigations
cp compose.yaml new-mitigations
tar cvfz new-mitigations.tar.gz new-mitigations/
rm -rf new-mitigations
