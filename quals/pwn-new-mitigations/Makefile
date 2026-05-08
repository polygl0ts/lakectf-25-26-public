all:
	gcc chal.c -o chal -fhardened
	patchelf --set-rpath . ./chal
	patchelf --set-interpreter ./ld-linux-x86-64.so.2 ./chal
