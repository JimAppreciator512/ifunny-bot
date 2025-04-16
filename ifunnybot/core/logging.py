import logging
import sys
from datetime import datetime


class HighPassFilter(logging.Filter):
    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return record.levelno >= self.level


# filename
filename = f"logs/{int(datetime.utcnow().timestamp())}-funnybot.log"

# creating a Logger
Logger = logging.getLogger("FunnyBot")
Logger.setLevel(logging.DEBUG)

# creating formatter
fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)-7s: %(message)s")

# stdout handler
std = logging.StreamHandler(sys.stdout)
std.setFormatter(fmt)
std.setLevel(logging.DEBUG)

# file handler
fd = logging.FileHandler(filename, mode="w")
fd.setFormatter(fmt)
fd.setLevel(logging.INFO)

# adding handlers
Logger.addHandler(std)
Logger.addHandler(fd)
