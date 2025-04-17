import io
from typing import Optional

import requests
import pyfsig
from PIL import Image, ImageOps

from ifunnybot.types.response import Response
from ifunnybot.data.signatures import IFUNNY_SIGS


def retrieve_content(url: str) -> Optional[Response]:
    """
    Grabs the content from the iFunny CDN i.e., videos, images and gifs.
    """

    # getting the post, assuming that it is a proper link
    response = None
    try:
        response = requests.get(url, allow_redirects=False)
    except Exception:
        # got an error
        # Logger.error(
        #     f"Failed to retrieve content from {url}, most likely no internet connection or a malformed url."
        # )
        return None

    # checking if we actually have a response
    if not response:
        # Logger.error(f"Did not receive a response from {url}.")
        return None

    # do we have a body?
    if not response.content:
        # Logger.error(f"Response from {url} does not have a content body, aborting.")
        return None

    # looking at the file type from the header
    sig = None
    sigs = pyfsig.find_matches_for_file_header(response.content, signatures=IFUNNY_SIGS)

    # checking the number of signatures
    match len(sigs):
        case 0:
            # Logger.warn(f"pyfsig failed to determine the type of the file.")
            pass
        case 1:
            # Logger.debug(f"Signature of the file: {sigs[0]}")
            sig = sigs[0]
        case _:
            # Logger.warn(
            #     f"Error discerning the file signature from the response, number of signatures: {len(sigs)}"
            # )
            # Logger.warn(f"Picking the first signature: {sigs}")
            sig = sigs[0]

    # creating new Response object
    resp = Response(io.BytesIO(response.content), url, sig, response)

    # logging
    # Logger.debug(resp)

    # returning the response object
    return resp


def crop_convert(_bytes: io.BytesIO, crop=False, format="PNG") -> io.BytesIO:
    """
    Converts a byte stream of type `io.BytesIO` to the specified format using PIL,
    also crops the bottom 20 pixels out of the image to remove the dreaded iFunny
    watermark.

    This function does not check whether or not `_bytes` is an actual image,
    if you try to pass in something that isn't an image, you'll most likely get an
    error.
    """

    # new buffer
    nbuf = io.BytesIO()

    # turning bytes into an image
    _image = Image.open(_bytes)

    # checking the file type
    if _image.format == None:
        pass
        # Logger.warn(f"PIL could not discern what file type the image is.")

    # cropping & the image
    if crop:
        _image = ImageOps.crop(_image, (0, 0, 0, 20))
        # Logger.debug("Cropped watermark from image.")

    # converting the image
    _image.save(nbuf, format=format)

    # logging
    # Logger.debug(f"Converted '{_image.format}' to 'PNG'.")

    # cleanup
    _bytes.close()
    del _bytes
    nbuf.seek(0)

    # returning the new buffer
    return nbuf
