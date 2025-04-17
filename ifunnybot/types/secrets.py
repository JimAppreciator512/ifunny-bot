"""
This class contains a nice wrapper around all the secrets for the bot.
"""

from typing import Any


class Secrets:
    """
    This class contains a nice wrapper around all the secrets for the bot.
    """

    def __init__(self, env: dict[str, Any]):
        # from the .env file
        self.token: str = env.get("TOKEN", None)
        self.client_id: int = env.get("CLIENTID", None)
        self.guild_id: int = env.get("GUILDID", None)
        self.error_channel: int = env.get("ERRORCHANNEL", None)

        # perform self validation
        assert self._validate() is True

    def _validate(self) -> bool:
        # checking the values
        if self.token is None:
            raise ValueError("TOKEN in the .env file is not set.")
        if self.client_id is None:
            raise ValueError("CLIENTID in the .env file is not set.")
        if self.guild_id is None:
            raise ValueError("GUILDID in the .env file is not set.")
        if self.error_channel is None:
            raise ValueError("ERRORCHANNEL in the .env file is not set.")

        # casting to types
        self.client_id = int(self.client_id)
        self.guild_id = int(self.guild_id)
        self.error_channel = int(self.error_channel)

        return True

    def __repr__(self) -> str:
        return f"<Secrets: token={self.token[:3]}***, client_id={str(self.client_id)[:3]}***, guild_id={str(self.guild_id)[:3]}***, error_channel={str(self.error_channel)[:3]}***>"
