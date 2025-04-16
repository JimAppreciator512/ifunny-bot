import re
from typing import Optional, TYPE_CHECKING

# dear fucking God never remove this
if TYPE_CHECKING:
    from ifunnybot.types.post import Post

FILENAME_PATTERN = r"co\/\w+\/([0-9a-f]*)(?:_\d)?\.(\w{3,4})$"


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
