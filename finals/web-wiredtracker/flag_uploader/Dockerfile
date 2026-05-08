FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
        python3 python3-pip python3-pymysql python3-requests wget \
    && rm -rf /var/lib/apt/lists/*

RUN if [ "$(arch)" = "aarch64" ]; then \
        wget https://github.com/autobrr/mkbrr/releases/download/v1.21.0/mkbrr_1.21.0_linux_arm64.deb -O /tmp/mkbrr.deb; \
    else \
        wget https://github.com/autobrr/mkbrr/releases/download/v1.21.0/mkbrr_1.21.0_linux_amd64.deb -O /tmp/mkbrr.deb; \
    fi && \
    dpkg -i /tmp/mkbrr.deb && \
    rm /tmp/mkbrr.deb

WORKDIR /app
COPY upload_flag.py *.mp3 /app/

CMD [ "python3", "upload_flag.py" ]
