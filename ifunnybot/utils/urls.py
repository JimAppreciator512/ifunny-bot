import re
from typing import Optional, Any

from ifunnybot.types.post_type import PostType

# regular expressions
IFUNNY_URL_REGEX = (
    r"(https:\/\/(br\.)?ifunny.co\/(picture|video|gif|meme|user)\/[\w|-]+(\?s=cl)?)"
)
IFUNNY_USER_URL_REGEX = r"https:\/\/(br\.)?ifunny.co\/user\/([\w|-|_]+)"
IFUNNY_DATATYPE = r"(picture|video|gif|meme|user)"

# constants
IFUNNY_NO_PFP = "https://play-lh.googleusercontent.com/Wr4GnjKU360bQEFoVimXfi-OlA6To9DkdrQBQ37CMdx1Kx5gRE07MgTDh1o7lAPV1ws"


def username_to_url(username: str) -> str:
    """Converts a username into a proper iFunny URL"""
    return f"https://ifunny.co/user/{username}"


def get_url(text: str) -> Optional[list[str]]:
    """
    Scrapes the ifunny.co url from the `text` input.
    """

    # using re.search because re.match is fucking stupid
    m = re.findall(IFUNNY_URL_REGEX, text, re.DOTALL)

    # returning a match object
    if len(m) > 0:
        return list(map(lambda x: x[0], m))
    return None


def has_url(text: str) -> bool:
    """
    Returns true if the text has an ifunny url, false otherwise.
    """

    return get_url(text) is not None


def get_datatype(url: str) -> Optional[PostType]:
    """
    Gets the datatype of the post from the iFunny url.
    """

    if url is None:
        return None

    # using re.search because re.match is fucking stupid
    m = re.search(IFUNNY_DATATYPE, url)

    # testing for a type
    if m:
        return PostType.value_of(m.group(0))
    return None


def get_username_from_url(url: str) -> Optional[str]:
    """
    Gets the name of a user from the url.
    """

    if not has_url(url):
        return None

    # using re.search
    m = re.search(IFUNNY_USER_URL_REGEX, url)

    # testing for a match
    if m:
        return m.group(2)
    return None
