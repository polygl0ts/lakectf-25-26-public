FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

ENV HOST=0.0.0.0
ENV PORT=9999

EXPOSE 9999

CMD ["python", "server.py"]
