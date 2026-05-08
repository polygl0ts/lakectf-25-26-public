FROM ubuntu:24.04@sha256:d22e4fb389065efa4a61bb36416768698ef6d955fe8a7e0cdb3cd6de80fa7eec AS builder
FROM pwn.red/jail@sha256:ee52ad5fd6cfed7fd8ea30b09792a6656045dd015f9bef4edbbfa2c6e672c28c

COPY --from=builder / /srv

# Change `./source/` to `./` if you want to run the Dockerfile.
COPY ./source/run /srv/app/run
COPY ./source/libc.so.6 /srv/app/libc.so.6
COPY ./source/ld-linux-x86-64.so.2 /srv/app/ld-linux-x86-64.so.2
COPY ./source/flag.txt /srv/app/flag.txt
COPY ./source/rooftop /srv/app/rooftop
COPY ./source/stairwell /srv/app/stairwell

RUN chmod 755 /srv/app/run
RUN chmod 755 /srv/app/rooftop
RUN chmod 755 /srv/app/stairwell
RUN chmod 755 /srv/app/libc.so.6
RUN chmod 755 /srv/app/ld-linux-x86-64.so.2
RUN chmod 744 /srv/app/flag.txt

ENV JAIL_TIME=3000
ENV JAIL_MEM=100M
ENV JAIL_TMP_SIZE=100M
