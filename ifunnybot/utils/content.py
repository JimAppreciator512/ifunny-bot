import io
from typing import Optional

import requests
from PIL import Image

from ifunnybot.core.logging import Logger

# magic bytes for confirming file types
WEBM_MAGIC_BYTES = ['\x1a', '\x45', '\xdf']
GIF_MAGIC_BYTES = ['\x47', '\x49', '\x46']

def retrieve_content(url: str) -> Optional[io.BytesIO]:
    # getting the post, assuming that it is a proper link
    response = None
    try:
        response = requests.get(url, allow_redirects=False)
    except Exception:
        # got an error
        Logger.error(f"Failed to retrieve content from {url}, most likely no internet connection or a malformed url.")
        return None

    # logging
    Logger.debug(f"Response from {url}: {response.reason}.")

    # checking if we actually have a response
    if not response:
        Logger.error(f"Did not receive a response from {url}.")
        return None
    if not response.content:
        Logger.error(f"Response from {url} does not have a content body, aborting.")
        return None

    # casting response into a byte array
    buffer = io.BytesIO(response.content)

    # logging
    Logger.debug(f"Response size: {len(response.content)}, saved size: {buffer.getbuffer().nbytes}")

    # saving the response as a byte array
    return buffer 

def convert_image_to_png(_bytes: io.BytesIO) -> io.BytesIO:
    # new buffer
    nbuf = io.BytesIO()

    # turning bytes into an image
    _image = Image.open(_bytes)
    _image.save(nbuf, format="PNG")

    # logging
    Logger.debug(f"Converted '{_image.format}' to 'PNG'.")

    # cleanup
    _bytes.close()
    del _bytes
    nbuf.seek(0)

    # returning the new buffer
    return nbuf

