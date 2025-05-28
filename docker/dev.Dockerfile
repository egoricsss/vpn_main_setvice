FROM python:3.13-alpine

RUN pip install --no-cache-dir watchdog

WORKDIR /app

COPY ../requirements.txt .

RUN pip install -r --no-cache-dir requirements.txt

COPY . .