import logging
import sys

# creating a Logger
Logger = logging.getLogger("FunnyBot")
Logger.setLevel(logging.INFO)
Logger.addHandler(logging.StreamHandler(sys.stdout))

