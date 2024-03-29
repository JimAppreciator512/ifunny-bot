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
Logger.addFilter(HighPassFilter(logging.DEBUG))

# creating formatter
fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)-7s: %(message)s")

# stdout handler
std = logging.StreamHandler(sys.stdout)
std.setFormatter(fmt)
std.setLevel(logging.ERROR)
std.addFilter(HighPassFilter(logging.INFO))

# file handler
fd = logging.FileHandler(filename, mode="w")
fd.setFormatter(fmt)
fd.setLevel(logging.DEBUG)
fd.addFilter(HighPassFilter(logging.DEBUG))

# adding handlers
Logger.addHandler(std)
Logger.addHandler(fd)

