import re
from typing import Optional

from ..types.post_type import PostType

# regular expressions
ifunny_url_pattern = r"(https:\/\/ifunny.co\/(picture|video|gif|meme)\/(.*){1,20}(\?.*){0,20})"
ifunny_type_pattern = r"(picture|video|gif|meme)"

# CSS selectors
html_selectors = {
        PostType.PICTURE: ["div._3ZEF > img", "src"],
        PostType.VIDEO: ["div._3ZEF > div > video", "data-src"],
        PostType.GIF: ['head > link[as="image"]', "href"]
        }

def findiFunnyUrl(url: str) -> Optional[str]:
    m = re.match(ifunny_url_pattern, url)

    # returning a match object
    if m:
        return m.group(0)
    else:
        return m

def hasiFunnyUrl(url: str) -> bool:
    return findiFunnyUrl(url) != None

def iFunnyDatatype(url: str) -> Optional[PostType]:
    m = re.match(ifunny_type_pattern, url)

    # testing for a type
    if m:
        return PostType.value_of(m.group(0))
    else:
        return None

