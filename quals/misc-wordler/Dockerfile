FROM docker.io/library/ubuntu:22.04@sha256:0e5e4a57c2499249aafc3b40fcd541e9a456aab7296681a3994d631587203f97 as builder

RUN apt-get update && \
    apt install -y python3

RUN useradd -u 1000 jail

FROM pwn.red/jail@sha256:ee52ad5fd6cfed7fd8ea30b09792a6656045dd015f9bef4edbbfa2c6e672c28c

COPY --from=builder / /srv

COPY --chmod=0755 wordle.py /srv/app/run
COPY --chmod=0644 word_list.txt /srv/app/word_list.txt
COPY --chmod=0644 flag.py /srv/app/flag.py


RUN chmod 755 /srv/app/run


ENV JAIL_TIME 120
ENV JAIL_MEM 100M