# syntax=docker/dockerfile:latest

FROM docker.io/library/ubuntu@sha256:562456a05a0dbd62a671c1854868862a4687bf979a96d48ae8e766642cd911e8 as builder

# Enable APT package caching
RUN rm -f /etc/apt/apt.conf.d/docker-clean && \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# Install packages
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends make g++

# Add files
COPY Makefile /tmp/Makefile
COPY silent-lake.cpp /tmp/silent-lake.cpp

# Compile
WORKDIR /tmp
RUN make


FROM docker.io/library/ubuntu@sha256:562456a05a0dbd62a671c1854868862a4687bf979a96d48ae8e766642cd911e8 as base

# Enable APT package caching
RUN rm -f /etc/apt/apt.conf.d/docker-clean && \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# Install packages
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends python3 binutils
RUN useradd -u 1000 jail || true


FROM pwn.red/jail@sha256:ee52ad5fd6cfed7fd8ea30b09792a6656045dd015f9bef4edbbfa2c6e672c28c

COPY --from=base / /srv
COPY --chmod=0755 chal.py /srv/app/run
COPY --chmod=0755 --from=builder /tmp/silent-lake /srv/app/silent-lake
COPY --chmod=0644 flag.txt /srv/app/flag

ENV JAIL_TIME 120
ENV JAIL_CONNS_PER_IP 5
ENV JAIL_MEM 20M
ENV JAIL_TMP_SIZE 20M
