obj-m += furrow.o
EXTRA_CFLAGS += -g
KERNEL_DIR="~/opt/linux/"


module: furrow.c
	bear -- make -C $(KERNEL_DIR) M=$(PWD) HOSTCC=gcc-11 CC=gcc-11 modules
	cp furrow.ko rootfs/furrow.ko

clean_module:
	make -C $(KERNEL_DIR) M=$(PWD) clean

