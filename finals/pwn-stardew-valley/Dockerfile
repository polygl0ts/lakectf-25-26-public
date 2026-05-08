FROM archlinux@sha256:8435d30c1462f94345c3894ebbeaeecd658fcb284aa41b0bcc5f88728933447f AS builder

RUN echo 'CleanMethod = KeepCurrent' >> /etc/pacman.conf

RUN --mount=type=cache,target=/var/cache/pacman/pkg,sharing=locked \
    pacman -Syu --noconfirm && \
    pacman -S --noconfirm --needed qemu-system-x86

FROM pwn.red/jail@sha256:ee52ad5fd6cfed7fd8ea30b09792a6656045dd015f9bef4edbbfa2c6e672c28c

COPY --from=builder / /srv
COPY ./deploy/run /srv/app/run
COPY ./deploy/run.sh /srv/app/run.sh
COPY ./deploy/rootfs.cpio /srv/app/rootfs.cpio
COPY ./deploy/bzImage /srv/app/bzImage

RUN chmod 755 /srv/app/run && \
    chmod 755 /srv/app/run.sh && \
    chmod 744 /srv/app/rootfs.cpio && \
    chmod 744 /srv/app/bzImage

ENV JAIL_TIME=3000
ENV JAIL_MEM=300M
ENV JAIL_CPU=1000

