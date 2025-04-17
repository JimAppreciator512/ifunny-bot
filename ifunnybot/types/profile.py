"""
This file contains an object representing a profile from iFunny.
"""

import io
from typing import Optional

# from ifunnybot.core.logging import Logger
from ifunnybot.utils.content import retrieve_content, crop_convert


class Profile(object):
    """
    This profile represents a profile/user on iFunny.
    """

    # CSS selectors
    ICON_SEL = "div.Du6F > span.uHyU > span.rL50 > img"
    USERNAME_SEL = "div.pkOr > div.zWwJ"
    DESCRIPTION_SEL = "div.pkOr > div.aSGm"
    SUBSCRIBERS_SEL = "div.pkOr > div.brxh > a:nth-child(1)"
    SUBSCRIPTIONS_SEL = "div.pkOr > div.brxh > a:nth-child(2)"
    FEATURES_SEL = "div.pkOr > div.x6q6"

    def __init__(
        self,
        username: str = "",
        icon_url: Optional[str] = "",
        subscribers: str = "",
        subscriptions: str = "",
        features: str = "",
        description: str = "",
    ):

        # saving fields
        self._username: str = username
        self._icon_url: Optional[str] = icon_url
        self._subscribers: str = subscribers
        self._subscriptions: str = subscriptions
        self._features: str = features
        self._description: str = description

        # remove cropping
        self._remove_icon_cropping()

    def __repr__(self) -> str:
        return f"<Profile: {self._username}, {self._subscribers} subscribers, {self._features} features>"

    def retrieve_icon(self) -> Optional[io.BytesIO]:
        """Retrieves the icon of the user."""
        if self._icon_url is None:
            return None

        if not (resp := retrieve_content(self._icon_url)):
            # Logger.error(f"Couldn't retrieve the icon of user {self}")
            return None

        return crop_convert(resp.bytes, crop=False)

    def _remove_icon_cropping(self):
        """This removes the cropping functionality from the URL."""
        if self._icon_url is None:
            return
        self._icon_url = self._icon_url.replace(":square,resize:100x,quality:90x75", "")

    @property
    def username(self) -> str:
        """Returns the username."""
        return self._username

    @username.setter
    def username(self, value: str):
        """Sets the number of username to `value`"""
        self._username = str(value)

    @property
    def profile_url(self) -> str:
        """Returns the URL of the profile."""
        return f"https://ifunny.co/user/{self._username}"

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
    def icon_url(self) -> Optional[str]:
        """Returns the URL of the profile picture of the user."""
        return self._icon_url

    @icon_url.setter
    def icon_url(self, value: str):
        """Sets the number of icon_url to `value`"""
        self._icon_url = str(value)
        self._remove_icon_cropping()

    @property
    def description(self) -> str:
        """Returns the user's description."""
        return self._description

    @description.setter
    def description(self, value: str):
        """Sets the number of description to `value`"""
        self._description = str(value)
