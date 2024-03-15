"""
This file contains the bot object.
"""

import logging
import discord
from discord import app_commands

class FunnyBot(discord.Client):
    def __init__(self, *, intents: discord.Intents, guildId: int = 0, logger: logging.Logger) -> None:
        super().__init__(intents=intents)

        # saving the reference to the logger
        self._log = logger

        # the tree variable holds slash commands
        self.tree = app_commands.CommandTree(self)

        # saving the target guild id
        if guildId:
            self._log.info("Starting bot in development mode")
            self._guild = discord.Object(id=guildId)
        else:
            self._guild = None

    async def setup_hook(self) -> None:
        # dispatching commands
        if self._guild:
            self._log.info(f"Copying commands to development server.")
            self.tree.copy_global_to(guild=self._guild)
        await self.tree.sync(guild=self._guild)
        
        # logging
        self._log.info("Set up self")

