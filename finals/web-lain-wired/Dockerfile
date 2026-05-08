FROM node:20-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PUPPETEER_SKIP_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
ENV BODY_LIMIT=8mb

RUN apt-get update \
    && apt-get install -y --no-install-recommends chromium \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY challenge/package.json /app/package.json
RUN npm install --omit=dev

COPY challenge /app

EXPOSE 1337

CMD ["node", "app.js"]
