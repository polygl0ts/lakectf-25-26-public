FROM docker.io/library/ubuntu:22.04@sha256:0e5e4a57c2499249aafc3b40fcd541e9a456aab7296681a3994d631587203f97 AS builder

RUN apt-get update && \
    apt install -y python3 python3-pip

RUN python3 -m pip install sympy pycryptodome rich

RUN useradd -u 1000 jail

FROM pwn.red/jail@sha256:ee52ad5fd6cfed7fd8ea30b09792a6656045dd015f9bef4edbbfa2c6e672c28c

COPY --from=builder / /srv


COPY --chmod=0644 ./secret.py /srv/app/secret.py
COPY --chmod=0644 ./fancy.py /srv/app/fancy.py
COPY --chmod=0755 ./chall.py /srv/app/run

RUN chmod 755 /srv/app /srv/app/run


ENV JAIL_TIME 300
ENV JAIL_MEM 400M