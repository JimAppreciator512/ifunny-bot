# syntax=docker/dockerfile:1
FROM python:3.11

# app workdir
WORKDIR /app

# copying files
COPY . /app/

# building
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# running the app
CMD ["python3", "main.py"]

