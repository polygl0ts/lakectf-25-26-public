FROM python:slim AS app
RUN pip install --no-cache-dir progress

FROM pwn.red/jail
COPY --from=app / /srv

COPY pow.py srv/app/run
COPY flag.txt srv/app/flag.txt
RUN chmod +x /srv/app/run
RUN chmod 644 /srv/app/flag.txt

ENV JAIL_POW=180000
