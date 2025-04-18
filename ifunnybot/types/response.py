"""
This file is for an object that contains information about the response
from the iFunny CDN.
"""

import io
from typing import Optional

import requests
from pyfsig.interface import FileSignature


class Response(object):
    """
    Contains information about the response from the iFunny CDN.
    """

    def __init__(
        self,
        bytes_: io.BytesIO,
        url: str,
        type_: Optional[FileSignature],
        response: requests.Response,
    ):
        if not bytes_:
            raise ValueError("_bytes wasn't defined during creation.")
        if not url:
            raise ValueError("_url wasn't defined during creation.")
        if not response:
            raise ValueError("_response wasn't defined during creation.")

        self._bytes = bytes_
        self._type = type_
        self._url = url
        self._response = response

    @property
    def reason(self) -> str:
        """
        A shorthand to get the HTTP reason of the response
        """
        return self._response.reason

    @property
    def raw(self) -> requests.Response:
        """
        The raw response from `requests`.
        """
        return self._response

    @property
    def url(self) -> str:
        """
        Gets the content URL that the response originated from.
        """
        return self._url

    @property
    def type(self) -> Optional[FileSignature]:
        """
        Gets the type of the response i.e., the "content-type" from the headers.
        """
        return self._type

    @property
    def bytes(self) -> io.BytesIO:
        """
        Gets the buffer containing the post itself.
        """
        return self._bytes

    @bytes.setter
    def bytes(self, nbuf):
        """
        Sets the internal buffer.
        """
        self._bytes = nbuf

    def __repr__(self) -> str:
        if self._type:
            return f"<Response({self.reason}): url={self._url}, type={self._type.file_extension}, {self._bytes.getbuffer().nbytes / 1_000_000} MB>"
        return f'<Response({self.reason}): url={self._url}, type="???", {self._bytes.getbuffer().nbytes / 1_000_000} MB>'

    def __str__(self) -> str:
        return self.__repr__()
