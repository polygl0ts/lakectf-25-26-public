DOCKER ?= docker

.PHONY: all build run

all: build

build:
	$(DOCKER) compose build --pull stackception-builder
	$(DOCKER) compose run --rm stackception-builder cp -av /out/bin/stackception-1 /mnt/
	$(DOCKER) compose run --rm stackception-builder cp -av /out/bin/stackception-2 /mnt/
	$(DOCKER) compose run --rm stackception-builder cp -av /out/bin/stackception-3 /mnt/
	$(DOCKER) compose run --rm stackception-builder cp -av /out/bin/stackception-asm /mnt/
	$(DOCKER) compose run --rm stackception-builder cp -av /lib/x86_64-linux-gnu/libc.so.6 /mnt/
	$(DOCKER) compose run --rm stackception-builder cp -av /lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 /mnt/

run:
	$(DOCKER) compose up -d --build stackception
