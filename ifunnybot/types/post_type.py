from enum import Enum

class PostType(Enum):
    PICTURE = 0
    VIDEO = 1
    GIF   = 2
    MEME  = 3

    @staticmethod
    def value_of(string: str):
        match string:
            case "picture":
                return PostType.PICTURE
            case "video":
                return PostType.VIDEO
            case "gif":
                return PostType.GIF
            case "meme":
                return PostType.MEME
            case _:
                return None
    
    def __str__(self):
        match self.value:
            case 0:
                return "picture"
            case 1:
                return "video"
            case 2:
                return "gif"
            case 3:
                return "meme"
            case _:
                raise TypeError(f"Tried to convert invalid enum value to string: {self.value}")

