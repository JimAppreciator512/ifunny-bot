"""
This file contains an object representing a post from iFunny.
"""

import io
from typing import Optional

from ifunnybot.types.post_type import PostType
from ifunnybot.types.response import Response
from ifunnybot.utils.content import crop_convert
from ifunnybot.utils.urls import (
    username_to_url,
    remove_icon_cropping,
    remove_image_cropping,
)


class Post(object):
    """
    Represents a post on iFunny.
    """

    # this has the canonical url which has the proper datatype
    CANONICAL_SEL = ("meta[property='og:url']", "content")

    # these point to some CDN
    PICTURE_SEL = ("meta[property='og:image']", "content")
    VIDEO_SEL = ("meta[property='og:video:url']", "content")
    GIF_SEL = ("link[rel=preload][as=image]", "href")

    # other metadata
    AUTHOR_SEL = ("meta[name='author']", "content")
    ICON_SEL = (  # this can fail! users might not have icons!
        "div > a > img.MmRx.xY6H.gsQw.YDCg",
        "data-src",
    )
    LIKES_SEL = "div > button:nth-child(3) > span > span"
    COMMENTS_SEL = "div > button:nth-child(4) > span > span"

    def __init__(
        self,
        likes: str = "",
        comments: str = "",
        author: str = "",
        url: str = "",
        post_type: PostType = PostType.MEME,
        content_url: str = "",
        icon_url: Optional[str] = "",
    ):
        # computed
        self._post_type: PostType = post_type
        self._url: str = url

        # parsed from the html
        self._likes: str = likes
        self._comments: str = comments
        self._author: str = author
        self._content_url: str = remove_image_cropping(content_url)
        self._icon_url: Optional[str] = icon_url  # using the setter

        # cropping if not none
        if self._icon_url is not None:
            self._icon_url = remove_icon_cropping(self._icon_url)

        # programmatically filled
        self._response: Response = None  # type: ignore

    def __repr__(self) -> str:
        if self._response:
            return f"<Post: {self._post_type}@{self._url} by {self._author}, type: {self._response or 'undefined'}>"
        return f"<Post: {self._post_type}@{self._url} by {self._author}>"

    def check_datatype(self):
        """
        This function checks whether or not the content requested from iFunny
        is actually what it says it is i.e., a gif is a gif and not an mp4.

        If the function finds that the datatype is incorrect, as of now, it will
        only change the internal `self._post_type` enum to match and NOT convert.
        """

        # this function doesn't actually do anything yet
        raise NotImplementedError("This function isn't implemented yet.")

    def crop_watermark(self):
        """Removes the iFunny watermark from images."""

        # checking the post type first
        if self._post_type != PostType.PICTURE:
            raise TypeError(
                f"Tried to crop something that wasn't an image: {self._post_type}"
            )

        self._response.bytes = crop_convert(self._response.bytes, crop=True)

    def username_to_url(self) -> str:
        """Returns the full URL of op."""
        return username_to_url(self._author)

    def validate(self) -> bool:
        """
        Validates the Object. Returns true on success,
        throws a ValueError otherwise.
        """
        if self._likes is None or not isinstance(self._likes, str):
            raise ValueError(f"likes is None or not str, was {self._likes}")
        if self._comments is None or not isinstance(self._comments, str):
            raise ValueError(f"comments is None or not str, was {self._comments}")
        if self._author is None or not isinstance(self._author, str):
            raise ValueError(f"username is None or not str, was {self._author}")
        if self._url is None or not isinstance(self._url, str):
            raise ValueError(f"url is None or not str, was {self._url}")
        if self._post_type is None or not isinstance(self._post_type, PostType):
            raise ValueError(
                f"post_type is None or not PostType, was {self._post_type}"
            )
        if self._content_url is None or not isinstance(self._content_url, str):
            raise ValueError(f"content_url is None or not str, was {self._content_url}")
        if self._response is None or not isinstance(self._response, Response):
            raise ValueError(f"content is None or not Response, was {self._response}")
        return True

    @property
    def content(self) -> io.BytesIO:
        """Returns the actual content in bytes."""
        return self._response.bytes

    @property
    def response(self) -> Response:
        return self._response

    @response.setter
    def response(self, o: Response):
        self._response = o

    @property
    def likes(self) -> str:
        """Returns the number of likes the post has at the time that the post was retrieved."""
        return self._likes

    @likes.setter
    def likes(self, value: str):
        """Sets the number of likes to `value`"""
        self._likes = str(value)

    @property
    def comments(self) -> str:
        """Returns the number of comments the post has at the time that the post was retrieved."""
        return self._comments

    @comments.setter
    def comments(self, value: str):
        """Sets the number of comments to `value`"""
        self._comments = str(value)

    @property
    def author(self) -> str:
        """Returns the author of the poster."""
        return self._author

    @author.setter
    def author(self, value: str):
        """Sets the number of author to `value`"""
        self._author = str(value)

    @property
    def url(self) -> str:
        """Returns the url of post."""
        return self._url

    @url.setter
    def url(self, value: str):
        """Sets the number of url to `value`"""
        self._url = str(value)

    @property
    def post_type(self) -> PostType:
        """Returns the type of post."""
        return self._post_type

    @post_type.setter
    def post_type(self, value: PostType):
        """Sets the number of post_type to `value`"""
        self._post_type = value

    @property
    def content_url(self) -> str:
        """Returns the content_url of post."""
        return self._content_url

    @content_url.setter
    def content_url(self, value: str):
        """Sets the number of content_url to `value`"""
        self._content_url = remove_image_cropping(str(value))

    @property
    def icon_url(self) -> Optional[str]:
        """Returns the icon_url of post."""
        return self._icon_url

    @icon_url.setter
    def icon_url(self, value: str):
        """Sets the number of icon_url to `value`"""
        self._icon_url = remove_icon_cropping(str(value))
