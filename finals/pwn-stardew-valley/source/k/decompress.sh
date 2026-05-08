#!/bin/bash

# If initramfs exists, rename it to rootfs
initramfs_file=$(ls initramfs.* 2>/dev/null | head -n 1)
if [[ -n "$initramfs_file" ]]; then
    extension="${initramfs_file#initramfs.}"
    rootfs_file="rootfs.$extension"
    echo "Renaming $initramfs_file to $rootfs_file"
    mv "$initramfs_file" "$rootfs_file"
fi

# Gunzip it if necessary
if [ -f rootfs.cpio.gz ]; then
    echo "Decompressing rootfs.cpio.gz with gunzip."
    gunzip rootfs.cpio.gz
fi

# Create rootfs dir
if [ -d rootfs ]; then
    echo "Deleting existing rootfs directory."
    rm -rf rootfs
fi
echo "Making a rootfs directory."
mkdir rootfs

# Unpack rootfs.cpio into the rootfs dir
if [ -f rootfs.cpio ]; then
    echo "Unpacking rootfs.cpio into the rootfs/ directory."
    (cd rootfs && cpio -idmv < ../rootfs.cpio)
else
    echo "Error: rootfs.cpio file not found."
    exit 1
fi

echo "Done!"
