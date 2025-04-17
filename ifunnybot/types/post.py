"""
This file contains an object representing a post from iFunny.
"""

import io
from typing import TYPE_CHECKING

from ifunnybot.types.post_type import PostType
from ifunnybot.core.logging import Logger
from ifunnybot.utils.content import crop_convert, retrieve_content
from ifunnybot.utils.urls import username_to_url

# dear fucking God never remove this
if TYPE_CHECKING:
    from ifunnybot.types.response import Response


class Post(object):
    """
    Represents a post on iFunny.
    """

    # this has the canonical url which has the proper datatype
    REAL_CONTENT_SEL = ("head > meta[property='og:url']", "content")
    AUTHOR_SEL = ("head > meta[name='author']", "content")

    # these point to some CDN
    PICTURE_SEL = ("head > meta[property='og:image']", "content")
    VIDEO_SEL = ("head > meta[property='og:video']", "content")
    GIF_SEL = ("head > link[rel='preload']", "href")

    def __init__(
        self,
        likes: str = "",
        comments: str = "",
        username: str = "",
        url: str = "",
        post_type: PostType = PostType.MEME,
        content_url: str = "",
        icon_url: str = "",
    ):

        # saving fields
        self._likes: str = likes
        self._comments: str = comments
        self._username: str = username
        self._url: str = url
        self._post_type: PostType = post_type
        self._content_url: str = content_url
        self._icon_url: str = icon_url
        self._content: Response = None  # type: ignore

    def __repr__(self) -> str:
        if self._content:
            return f"<Post: {self._post_type}@{self._url} by {self._username}, type: {self._content or 'undefined'}>"
        return f"<Post: {self._post_type}@{self._url} by {self._username}>"

    def retrieve_content(self):
        """Retrieves the content located at `self.content_url`."""

        # logging
        Logger.info(f"Retrieving content from CDN: {self._content_url}")

        # saving the response as a byte array
        if resp := retrieve_content(self._content_url):
            self._content = resp
        else:
            Logger.error(f"Failed to retrieve content from {self._content_url}.")

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

        self._content.bytes = crop_convert(self._content.bytes, crop=True)

    def username_to_url(self) -> str:
        """Returns the full URL of op."""
        return username_to_url(self._username)

    def validate(self) -> bool:
        """
        Validates the Object. Returns true on success,
        throws a ValueError otherwise.
        """
        if self._likes is None or not isinstance(self._likes, str):
            raise ValueError(f"likes is None or not str, was {self._likes}")
        if self._comments is None or not isinstance(self._comments, str):
            raise ValueError(f"comments is None or not str, was {self._comments}")
        if self._username is None or not isinstance(self._username, str):
            raise ValueError(f"username is None or not str, was {self._username}")
        if self._url is None or not isinstance(self._url, str):
            raise ValueError(f"url is None or not str, was {self._url}")
        if self._post_type is None or not isinstance(self._post_type, PostType):
            raise ValueError(
                f"post_type is None or not PostType, was {self._post_type}"
            )
        if self._content_url is None or not isinstance(self._content_url, str):
            raise ValueError(f"content_url is None or not str, was {self._content_url}")
        if self._icon_url is None or not isinstance(self._icon_url, str):
            raise ValueError(f"icon_url is None or not str, was {self._icon_url}")
        if self._content is None or not isinstance(self._content, Response):
            raise ValueError(f"content is None or not Response, was {self._content}")
        return True

    @property
    def content(self) -> io.BytesIO:
        """Returns the actual content in bytes."""
        return self._content.bytes

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
    def username(self) -> str:
        """Returns the username of the poster."""
        return self._username

    @username.setter
    def username(self, value: str):
        """Sets the number of username to `value`"""
        self._username = str(value)

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
        self._content_url = str(value)

    @property
    def icon_url(self) -> str:
        """Returns the icon_url of post."""
        return self._icon_url

    @icon_url.setter
    def icon_url(self, value: str):
        """Sets the number of icon_url to `value`"""
        self._icon_url = str(value)
