GLIBC_BUILD=$(HOME)/opt/glibc/build
GLIBC_INSTALL=$(GLIBC_BUILD)/install


# all: build_libc copy_libc rooftop stairwell
all: copy_libc rooftop stairwell

build_libc:
	cd $(HOME)/opt/glibc && git checkout glibc-2.43 && mkdir -p build && cd build && \
		mkdir -p install && ../configure --prefix "$(pwd)/install" --enable-bind-now && \
		make -j $(nproc) && make install

copy_libc:
	mkdir -p /tmp/
	cp "$(GLIBC_INSTALL)/lib/libc.so.6" /tmp/libc.so.6
	cp "$(GLIBC_INSTALL)/lib/ld-linux-x86-64.so.2" /tmp/ld-linux-x86-64.so.2

# gcc \
#   -L "$(GLIBC_INSTALL)/lib" \
#   -I "$(GLIBC_INSTALL)/include" \
#   -Wl,--rpath="$(GLIBC_INSTALL)/lib" \
#   -Wl,--dynamic-linker="$(GLIBC_INSTALL)/lib/ld-linux-x86-64.so.2" \
#   -std=c11 \
#   -o rooftop \
#   -g \
#   rooftop.c

rooftop: rooftop.c
	gcc \
	  -L "/tmp/" \
	  -I "$(GLIBC_INSTALL)/include" \
	  -Wl,--rpath="/tmp/" \
	  -Wl,--dynamic-linker="/tmp/ld-linux-x86-64.so.2" \
	  -std=c11 \
	  -o rooftop \
	  -g \
	  -Wl,-z,relro,-z,now \
	  rooftop.c

stairwell: stairwell.c
	gcc \
	  -L "/tmp/" \
	  -I "$(GLIBC_INSTALL)/include" \
	  -Wl,--rpath="/tmp/" \
	  -Wl,--dynamic-linker="/tmp/ld-linux-x86-64.so.2" \
	  -std=c11 \
	  -o stairwell \
	  -g \
	  -Wl,-z,relro,-z,now \
	  stairwell.c

clean:
	rm -f stairwell
	rm -f rooftop


