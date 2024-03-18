import io
from typing import Optional

import requests
from PIL import Image

from ifunnybot.core.logging import Logger

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

def convert_image_to_png(_bytes: io.BytesIO) -> io.BytesIO:
    # new buffer
    nbuf = io.BytesIO()

    # turning bytes into an image
    image = Image.open(_bytes)
    image.save(nbuf, format="PNG")

    # cleanup
    _bytes.close()
    del _bytes
    nbuf.seek(0)

    # returning the new buffer
    return nbuf

