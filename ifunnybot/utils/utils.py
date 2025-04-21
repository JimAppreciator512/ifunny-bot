import re
from typing import Optional, TYPE_CHECKING

# dear fucking God never remove this
if TYPE_CHECKING:
    from ifunnybot.types.post import Post

FILENAME_PATTERN = r"co\/\w+\/([0-9a-f]*)(?:_\d)?\.(\w{3,4})$"

# The SHA1 hash of the iFunny watermark.
# WATERMARK_MAGIC_HASH = "8545e508ee74bf3e046551137f294c25a132e28d"
WATERMARK_MAGIC_HASH = "5f64c68bed38a1e171a834e41a246796674ce922"


def sanitize_special_characters(text: str) -> str:
    """
    Escapes all of the special characters that discord uses.
    """

    illegal = ["\\", "*", "_", "|", "~", ">", "`"]
    sanitized = text

    # iterating over the illegal chars and escaping them
    for char in illegal:
        sanitized = sanitized.replace(char, "\\" + char)

    # returning the "sanitized" string
    return sanitized


def create_filename(post: "Post") -> Optional[str]:
    """
    Gets the name of the file from a `Post` object.
    """

    if not (match := re.search(FILENAME_PATTERN, post.content_url)):
        return None

    return match.group(1)


def spoof_headers() -> dict[str, str]:
    """
    This function returns a random collection of headers.
    """

    return {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "authority": "ifunny.co",
        "Cache-Control": "max-age=0",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
    }
