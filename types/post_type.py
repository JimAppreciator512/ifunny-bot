from enum import Enum
from typing import Optional

class PostType(Enum):
    PICTURE = 0
    VIDEO = 1
    GIF   = 2
    MEME  = 3

    @staticmethod
    def value_of(string: str) -> Optional[Enum]:
        match string:
            case "image":
                return PostType.PICTURE
            case "video":
                return PostType.VIDEO
            case "gif":
                return PostType.GIF
            case "meme":
                return PostType.MEME
            case _:
                return None

