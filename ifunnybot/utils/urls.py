import re
from typing import Optional, Any

from ifunnybot.types.post_type import PostType

# regular expressions
ifunny_url = r"(https:\/\/(br\.)?ifunny.co\/(picture|video|gif|meme)\/[\w|-]+(\?s=cl)?)"
ifunny_datatype = r"(picture|video|gif|meme)"

# constants
ifunny_no_pfp = "https://play-lh.googleusercontent.com/Wr4GnjKU360bQEFoVimXfi-OlA6To9DkdrQBQ37CMdx1Kx5gRE07MgTDh1o7lAPV1ws"

## function shorthands

def get_url(text: str) -> Optional[list[Any]]:
    """
    Scrapes the ifunny.co url from the `text` input.
    """

    # using re.search because re.match is fucking stupid
    m = re.findall(ifunny_url, text, re.DOTALL)

    # returning a match object
    if m:
        return list(map(lambda x: x[0], m))
    return m

def has_url(text: str) -> bool:
    """
    Returns true if the text has an ifunny url, false otherwise.
    """

    return get_url(text) != None

def get_datatype(url: str) -> Optional[PostType]:
    """
    Gets the datatype of the post from the iFunny url.
    """

    if not has_url(url):
        return None

    # using re.search because re.match is fucking stupid
    m = re.search(ifunny_datatype, url)

    # testing for a type
    if m:
        return PostType.value_of(m.group(0))
    return None
