import re
from typing import Optional, TYPE_CHECKING

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

