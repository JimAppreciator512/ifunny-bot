from ifunnybot.types.post_type import PostType

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

    def __repr__(self) -> str:
        return f"<Post: {self._post_type}@{self._url} by {self._username}, likes: {self._likes}, comments: {self._comments}>"

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

