import io
from typing import Optional

from ifunnybot.core.logging import Logger
from ifunnybot.utils.content import retrieve_content, convert_image_to_png

class Profile(object):
    def __init__(self, username: str = "", icon_url: str = "", subscribers: str = "",
                 subscriptions: str = "", features: str = "", description: str = ""): 

        # saving fields
        self._username: str = username
        self._icon_url: str = icon_url
        self._subscribers: str = subscribers
        self._subscriptions: str = subscriptions
        self._features: str = features
        self._description: str = description
        self._profile_url: str = f"https://ifunny.co/user/{self._username}"

    def __repr__(self) -> str:
        return f"<Profile: {self._username}, {self._subscribers} subscribers, {self._subscriptions} subscriptions, {self._features} features>"

    def retrieve_icon(self) -> Optional[io.BytesIO]:
        """Retrieves the icon of the user."""
        if not (_bytes := retrieve_content(self._icon_url)):
            Logger.error(f"Couldn't retrieve the icon of user {self}")
            return None
        return convert_image_to_png(_bytes)

    @property
    def username(self) -> str:
        """Returns the username."""
        return self._username

    @username.setter
    def username(self, value: str):
        """Sets the number of username to `value`"""
        self._username = str(value)
        self._profile_url = f"https://ifunny.co/user/{value}"

    @property
    def profile_url(self) -> str:
        """Returns the URL of the profile."""
        return self._profile_url

    @property
    def subscribers(self) -> str:
        """Returns the number of subscribers the user has."""
        return self._subscribers

    @subscribers.setter
    def subscribers(self, value: str):
        """Sets the number of subscribers to `value`"""
        self._subscribers = str(value)

    @property
    def subscriptions(self) -> str:
        """Returns the number of subscriptions the user has."""
        return self._subscriptions

    @subscriptions.setter
    def subscriptions(self, value: str):
        """Sets the number of subscriptions to `value`"""
        self._subscriptions = str(value)

    @property
    def features(self) -> str:
        """Returns the number of features the user has."""
        return self._features

    @features.setter
    def features(self, value: str):
        """Sets the number of features to `value`"""
        self._features = str(value)

    @property
    def icon_url(self) -> str:
        """Returns the URL of the profile picture of the user."""
        return self._icon_url

    @icon_url.setter
    def icon_url(self, value: str):
        """Sets the number of icon_url to `value`"""
        self._icon_url = str(value)

    @property
    def description(self) -> str:
        """Returns the user's description."""
        return self._description

    @description.setter
    def description(self, value: str):
        """Sets the number of description to `value`"""
        self._description = str(value)

