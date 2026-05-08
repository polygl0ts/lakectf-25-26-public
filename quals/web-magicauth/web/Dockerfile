FROM python:3.14-slim

RUN groupadd --system --gid 999 ctf \
 && useradd --system --gid 999 --uid 999 --create-home ctf

RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

RUN pip install 'fastapi[standard]==0.121.0' 'pyjwt==2.10.1' 'fastapi-cli==0.0.14'

COPY frontend/package.json /app/frontend/package.json
WORKDIR /app/frontend
RUN npm install
COPY frontend /app/frontend
RUN npm run build

COPY backend /app/backend

USER ctf
WORKDIR /app

CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "80", "backend"]
