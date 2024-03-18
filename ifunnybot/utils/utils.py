import re
import io
from typing import Optional, TYPE_CHECKING

import requests

from ifunnybot.core.logging import Logger

# dear fucking God never remove this
if TYPE_CHECKING:
    from ifunnybot.types.post import Post

filename_pattern = r"co\/\w+\/([0-9a-f]*)(?:_\d)?\.(\w{3,4})$"

def sanitize_discord(text: str) -> str:
    illegal = ["\\", "*", "_", "|", "~", ">", "`"]
    sanitized = text

    # iterating over the illegal chars and escaping them
    for char in illegal:
        sanitized = sanitized.replace(char, "\\" + char)

    # returning the "sanitized" string
    return sanitized

def create_filename(post: "Post") -> Optional[str]:
    if not (match := re.search(filename_pattern, post.content_url)):
        return None

    return match.group(1)

def retrieve_content(url: str) -> Optional[io.BytesIO]:
    # getting the post, assuming that it is a proper link
    response = None
    try:
        response = requests.get(url, allow_redirects=False)
    except Exception:
        return None

    buffer = io.BytesIO(response.content)

    # logging again
    Logger.debug(f"Response size: {len(response.content)}, saved size: {buffer.getbuffer().nbytes}")

    # saving the response as a byte array
    return buffer 

