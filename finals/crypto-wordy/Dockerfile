FROM ghcr.io/astral-sh/uv:alpine3.23

EXPOSE 1337

COPY server.py wordlist.txt pyproject.toml uv.lock /app/

ENV UV_NO_DEV=1

WORKDIR /app

RUN uv sync --locked

RUN apk add --no-cache socat

CMD ["socat", "-d", "TCP4-LISTEN:1337,reuseaddr,fork", "EXEC:'uv run server.py'"] 
