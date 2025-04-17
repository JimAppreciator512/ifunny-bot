import logging
import sys


def create_logger(filename: str, name: str = "FunnyBot") -> logging.Logger:
    """
    Creates a logger for whatever (primarily for the bot).
    """
    # creating a Logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # creating formatter
    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)-7s: %(message)s")

    # stdout handler
    std = logging.StreamHandler(sys.stdout)
    std.setFormatter(fmt)
    std.setLevel(logging.DEBUG)

    # file handler
    fd = logging.FileHandler(filename, mode="w")
    fd.setFormatter(fmt)
    fd.setLevel(logging.DEBUG)

    # adding handlers
    logger.addHandler(std)
    logger.addHandler(fd)

    return logger
