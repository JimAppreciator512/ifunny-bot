#!/bin/sh

# create venv
python -m venv venv --prompt="winedb"

# activate venv
source ./venv/bin/activate

# install requirements
python -m pip install -r requirements.txt

