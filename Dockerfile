# syntax=docker/dockerfile:1
FROM python:3.13 AS base

# app workdir
WORKDIR /app

# export directories
RUN mkdir -p /app/logs
RUN mkdir -p /app/pickles

# updating the packages
FROM base AS update
RUN apt update -y
RUN apt upgrade -y

# building base image
FROM update AS pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

FROM pip AS run
COPY . /app/

# running the app
CMD ["python3", "main.py", "-p", "/app/pickles", "-l", "/app/logs"]

