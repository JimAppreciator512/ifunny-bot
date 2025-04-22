"""
Various states for the bot and its functions.
"""

import enum

from PIL import Image


class Mode(enum.Enum):
    """
    Mode of running for the bot.
    """

    PRODUCTION = 0
    DEVELOPMENT = 1
    TESTING = 2  # for future use


class CropMethod(enum.StrEnum):
    """
    Enum of possible cropping methods.
    """

    AUTO = "auto"
    FORCE = "force"
    NOCROP = "no-crop"


class ImageFormat(enum.StrEnum):
    """
    Available image formats for posts to be saved as.
    """

    # from inspecting the PIL library
    # BLP, BMP, DIB, BUFR, PCX, DDS, EPS, GIF, GRIB, HDF5, PNG, JPEG2000, ICNS, ICO, IM, JPEG, TIFF, MPO, MSP, PALM, PDF, PPM, SGI, SPIDER, TGA, WEBP, WMF, XBM

    PNG = "PNG"
    JPEG = "JPEG"
    BMP = "BMP"
    GIF = "GIF"
    TIFF = "TIFF"
    WEBP = "WEBP"

    @staticmethod
    def is_supported(format_: "ImageFormat"):
        """
        Returns true if the ImageFormat is actually supported on this platform.
        """
        # loading everything if not loaded
        Image.init()

        # checking
        return format_.value in Image.SAVE
