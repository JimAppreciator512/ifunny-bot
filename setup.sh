#!/bin/sh

# creating the logs directory
mkdir logs

# creating files
touch .env
touch headers.pickle

echo "Created .env and headers.pickle, note that this bot won't work correctly unless you manually fill it out like how the `readme.md` says."

# create venv
python -m venv venv --prompt="funny-bot"

# activate venv
source ./venv/bin/activate

# install requirements
python -m pip install -r requirements.txt

