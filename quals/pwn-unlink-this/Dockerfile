FROM ubuntu:24.04@sha256:d22e4fb389065efa4a61bb36416768698ef6d955fe8a7e0cdb3cd6de80fa7eec AS builder

RUN rm -f /etc/apt/apt.conf.d/docker-clean && \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# Install packages
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends libjemalloc-dev 


#RUN useradd -u 1000 jail

FROM pwn.red/jail@sha256:ee52ad5fd6cfed7fd8ea30b09792a6656045dd015f9bef4edbbfa2c6e672c28c

COPY --from=builder / /srv
COPY unlink /srv/app/unlink
COPY run /srv/app/run
COPY flag /srv/app/flag

RUN chmod 755 /srv/app/run 
RUN chmod 755 /srv/app/unlink
RUN chmod 744 /srv/app/flag

ENV JAIL_TIME=300
ENV JAIL_MEM=20M

