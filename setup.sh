#!/usr/bin/env bash
set -e

# creating the logs directory
mkdir logs

# creating files
touch .env
touch headers.pickle

# logging for the user
echo "Created .env and headers.pickle, note that this bot won't work correctly unless you manually fill it out like how the `readme.md` says."

# create venv
python -m venv --prompt="funny-bot" venv

# activate venv
source ./venv/bin/activate

# install requirements
python -m pip install -r requirements.txt
