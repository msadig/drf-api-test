FROM python:3.8-slim

ENV LIBRARY_PATH=/lib:/usr/lib
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi6 \
    libffi-dev \
    python3-dev \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    gcc \
    libc-dev \
    bash \
    git \
    && pip3 install --upgrade pip \
    && pip3 --no-cache-dir install -r requirements.txt


WORKDIR /app

COPY ./app /app


