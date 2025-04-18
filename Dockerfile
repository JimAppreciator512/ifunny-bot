# syntax=docker/dockerfile:1
FROM python:3.11

# app workdir
WORKDIR /app

# export directories
RUN mkdir -p /app/logs
RUN mkdir -p /app/pickles

# copying files
COPY . /app/

# updating the container
RUN apt update -y
RUN apt upgrade -y

# installing pip packages
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# running the app
CMD ["python3", "main.py", "-p", "/app/pickles", "-l", "/app/logs"]
