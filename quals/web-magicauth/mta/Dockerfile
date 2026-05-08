FROM python:3.14-slim

RUN groupadd --system --gid 999 ctf \
 && useradd --system --gid 999 --uid 999 --create-home ctf

RUN pip install 'aiosmtpd==1.4.6'

COPY server.py /app/server.py

USER ctf
WORKDIR /app

CMD ["python", "server.py"]
