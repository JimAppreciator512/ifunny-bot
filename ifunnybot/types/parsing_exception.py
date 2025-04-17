"""
This type of error is meant to represent any errors that happen during HTML parsing.
"""


class ParsingError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
