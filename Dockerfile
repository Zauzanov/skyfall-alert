FROM python:3.11-slim

WORKDIR /app

# Basic OS deps for uvicorn performance; bs4/requests don't need build tools
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY static ./static

# Create data dir (mounted by docker-compose)
RUN mkdir -p /data

ENV PYTHONUNBUFFERED=1
