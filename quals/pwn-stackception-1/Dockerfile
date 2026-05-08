# syntax=docker/dockerfile:latest

###############################################################################
# Builder
###############################################################################
FROM docker.io/library/ubuntu@sha256:d22e4fb389065efa4a61bb36416768698ef6d955fe8a7e0cdb3cd6de80fa7eec AS builder

# Enable APT package caching
RUN rm -f /etc/apt/apt.conf.d/docker-clean && \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# Install packages
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        clang \
        lld \
        libclang-rt-dev \
        meson \
        ninja-build

# Build level 1
RUN --mount=type=bind,source=./src,target=/src,ro=true \
    mkdir -p /build && \
    meson setup \
        --native-file /src/meson-native \
        --buildtype=release \
        --strip \
        --prefix=/out \
        /build /src && \
    ninja -C /build install


###############################################################################
# Challenge (jail base)
###############################################################################
FROM docker.io/library/ubuntu@sha256:d22e4fb389065efa4a61bb36416768698ef6d955fe8a7e0cdb3cd6de80fa7eec AS base

# Enable APT package caching
RUN rm -f /etc/apt/apt.conf.d/docker-clean && \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-minimal

RUN useradd -u 1000 jail || true


###############################################################################
# Challenge (nsjail, level 1)
###############################################################################
FROM pwn.red/jail@sha256:ee52ad5fd6cfed7fd8ea30b09792a6656045dd015f9bef4edbbfa2c6e672c28c AS jail-1

COPY --from=base / /srv
COPY --chmod=0755 chall.py /srv/app/run
COPY --chmod=0755 stackception-1 /srv/app/stackception
COPY --chmod=0755 stackception-asm /srv/app/stackception-asm
COPY --chmod=0755 libc.so.6 /srv/lib/x86_64-linux-gnu/libc.so.6
COPY --chmod=0755 ld-linux-x86-64.so.2 /srv/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
COPY --chmod=0644 flag-1.txt /srv/app/flag.txt

ENV JAIL_TIME 60
ENV JAIL_CONNS_PER_IP 5
ENV JAIL_MEM 20M
ENV JAIL_TMP_SIZE 20M


###############################################################################
# Challenge (nsjail, level 2)
###############################################################################
FROM pwn.red/jail@sha256:ee52ad5fd6cfed7fd8ea30b09792a6656045dd015f9bef4edbbfa2c6e672c28c AS jail-2

COPY --from=base / /srv
COPY --chmod=0755 chall.py /srv/app/run
COPY --chmod=0755 stackception-2 /srv/app/stackception
COPY --chmod=0755 stackception-asm /srv/app/stackception-asm
COPY --chmod=0755 libc.so.6 /srv/lib/x86_64-linux-gnu/libc.so.6
COPY --chmod=0755 ld-linux-x86-64.so.2 /srv/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
COPY --chmod=0644 flag-2.txt /srv/app/flag.txt

ENV JAIL_TIME 60
ENV JAIL_CONNS_PER_IP 5
ENV JAIL_MEM 20M
ENV JAIL_TMP_SIZE 20M


###############################################################################
# Challenge (nsjail, level 3)
###############################################################################
FROM pwn.red/jail@sha256:ee52ad5fd6cfed7fd8ea30b09792a6656045dd015f9bef4edbbfa2c6e672c28c AS jail-3

COPY --from=base / /srv
COPY --chmod=0755 chall.py /srv/app/run
COPY --chmod=0755 stackception-3 /srv/app/stackception
COPY --chmod=0755 stackception-asm /srv/app/stackception-asm
COPY --chmod=0755 libc.so.6 /srv/lib/x86_64-linux-gnu/libc.so.6
COPY --chmod=0755 ld-linux-x86-64.so.2 /srv/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
COPY --chmod=0644 flag-3.txt /srv/app/flag.txt

ENV JAIL_TIME 60
ENV JAIL_CONNS_PER_IP 5
ENV JAIL_MEM 20M
ENV JAIL_TMP_SIZE 20M
