import io
from typing import Optional

import requests
from PIL import ImageOps, Image

from ifunnybot.core.logging import Logger
from ifunnybot.types.post import Post

def crop_watermark(post: Post) -> Optional[Image.Image]:
    """Removes the iFunny watermark from images."""

    # getting the post, assuming that it is a proper link
    response = None
    try:
        response = requests.get(post.content_url, allow_redirects=False)
    except Exception as e:
        Logger.error(f"There was an exception making a GET request to {post.content_url}: {e}")
        return None

    # turning the bytes into an image
    image = Image.open(io.BytesIO(response.content))

    # cropping & the image
    cropped = ImageOps.crop(image, (0, 0, 0, 20))

    # returning the image
    return cropped

