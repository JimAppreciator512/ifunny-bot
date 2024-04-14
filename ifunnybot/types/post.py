import io

from PIL import Image

from ifunnybot.core.logging import Logger
from ifunnybot.types.post_type import PostType
from ifunnybot.utils.content import retrieve_content

class Post(object):
    def __init__(self, likes: str = "", comments: str = "", username: str = "",
                 url: str = "", post_type:  PostType = PostType.MEME,
                 content_url:  str = "", icon_url: str = ""): 

        # saving fields
        self._likes: str = likes
        self._comments: str = comments
        self._username: str = username
        self._url: str = url
        self._post_type: PostType = post_type
        self._content_url: str = content_url
        self._icon_url: str = icon_url
        self._content: io.BytesIO = io.BytesIO()

    def __repr__(self) -> str:
        return f"<Post: {self._post_type}@{self._url} by {self._username}, likes: {self._likes}, comments: {self._comments}>"

    def retrieve_content(self):
        """Retrieves the content located at `self.content_url`."""

        # logging
        Logger.info(f"Retrieving content from CDN: {self._content_url}")

        # saving the response as a byte array
        if (_buf := retrieve_content(self._content_url)):
            self._content = _buf
        else:
            Logger.error(f"Failed to retrieve content from {self._content_url}.")
            return
        
        # checking the data type of the image
        self.check_datatype()

    def check_datatype(self):
        """
        This function checks whether or not the content requested from iFunny
        is actually what it says it is i.e., a gif is a gif and not an mp4.

        If the function finds that the datatype is incorrect, as of now, it will
        only change the internal `self._post_type` enum to match and NOT convert.
        """

        # checking if we actually have something to analyze
        if not self._content:
            Logger.error("Tried to analyze content of non-existant byte-array")
            return

        # checking type
        match self._post_type:
            case PostType.PICTURE:
                try:
                    Image.open(self._content)
                except Exception:
                    Logger.warn(f"The content from {self._content_url} isn't actually an image.")
            case PostType.GIF:
                pass
            case PostType.VIDEO:
                pass

        # updating type

    def crop_watermark(self):
        """Removes the iFunny watermark from images."""

        # logging
        Logger.info(f"Cropping watermark.")

        # checking the post type first
        if self._post_type != PostType.PICTURE:
            Logger.warn(f"Tried to crop something that wasn't an image: {self._post_type}")
            return

        # turning bytes into an image
        image = Image.open(self._content)

        # cropping & the image
        cropped = ImageOps.crop(image, (0, 0, 0, 20))

        # saving the image back into the bytes buffer
        # I hate this hack
        self._content.close()
        del self._content
        self._content = io.BytesIO()
        cropped.save(self._content, format="PNG")

        # cleanup
        image.close()
        cropped.close()
        del image, cropped

        # seeking back to the beginning because this fixes things
        self._content.seek(0)

    @property
    def content(self) -> io.BytesIO:
        return self._content

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

