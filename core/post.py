from ..types.post_type import PostType

class Post(object):
    def __init__(self, likes:int = 0, comments:int = 0, op:str = "",
                 url:str = "", post_type: PostType = PostType.OTHER, content_url: str = ""):

        # saving fields
        self._likes: int = likes
        self._comments: int = comments
        self._op: str = op
        self._url: str = url
        self._post_type: PostType = post_type
        self._content_url: str = content_url

        return

    @property
    def likes(self) -> int:
        """Returns the number of likes the post has at the time that the post was retrieved."""
        return self._likes

    @likes.setter
    def likes(self, value: int):
        """Sets the number of likes to `value`"""
        self._likes = int(value)

    @property
    def comments(self) -> int:
        """Returns the number of comments the post has at the time that the post was retrieved."""
        return self._comments

    @comments.setter
    def comments(self, value: int):
        """Sets the number of comments to `value`"""
        self._comments = int(value)

    @property
    def op(self) -> str:
        """Returns the username of the poster."""
        return self._op

    @op.setter
    def op(self, value: str):
        """Sets the number of op to `value`"""
        self._op = str(value)

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

