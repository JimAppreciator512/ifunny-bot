"""
All the possible states that the bot can be running in.
"""

import enum


class Mode(enum.Enum):
    PRODUCTION = 0
    DEVELOPMENT = 1
