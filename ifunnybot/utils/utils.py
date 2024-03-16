import re
from typing import Optional

from ifunnybot.types.post_type import PostType

# regular expressions
ifunny_url_pattern = r"(https:\/\/ifunny.co\/(picture|video|gif|meme)\/(.*){1,20}(\?.*){0,20})"
ifunny_type_pattern = r"(picture|video|gif|meme)"

def get_url(url: str) -> Optional[str]:
    # using re.search because re.match is fucking stupid
    m = re.search(ifunny_url_pattern, url)

    # returning a match object
    if m:
        return m.group(0)
    else:
        return m

def get_datatype(url: str) -> Optional[PostType]:
    # using re.search because re.match is fucking stupid
    m = re.search(ifunny_type_pattern, url)

    # testing for a type
    if m:
        return PostType.value_of(m.group(0))
    else:
        return None

