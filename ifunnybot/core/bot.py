"""
This file contains the bot object.
"""

from typing import Tuple, TYPE_CHECKING

import discord
from discord import app_commands

from ifunnybot.core.get_profile import (
    get_profile_by_name,
    get_username_from_url,
)
from ifunnybot.core.get_post import get_post
from ifunnybot.types.mode import Mode
from ifunnybot.types.secrets import Secrets
from ifunnybot.types.post_type import PostType
from ifunnybot.utils.urls import get_url, get_datatype
from ifunnybot.utils.utils import sanitize_special_characters, create_filename

if TYPE_CHECKING:
    # importing this as a type
    import logging


class FunnyBot(discord.Client):
    """
    The most elite Discord bot for iFunny posts yet.
    """

    def __init__(
        self, *, intents: discord.Intents, logger: "logging.Logger", secrets: Secrets, mode: Mode = Mode.PRODUCTION
    ) -> None:
        super().__init__(intents=intents)

        # saving variables
        self._logger = logger  # saving the reference to the logger
        self._tree = app_commands.CommandTree(
            self
        )  # the tree variable holds slash commands
        self._mode = mode
        self._secrets = secrets
        self._guild: discord.Object = discord.Object(
            id=self._secrets.guild_id, type=discord.abc.GuildChannel
        )

    # --- setup functions ---

    async def setup_hook(self):
        # logging
        self._logger.info(f"Starting bot in {self._mode.name} mode.")

        # publishing commands
        match self._mode:
            # if in development, dispatch commands to our testing server
            case Mode.DEVELOPMENT:
                # dispatching to the testing server
                self._tree.copy_global_to(guild=self._guild)

                # syncing commands to discord
                commands = await self._tree.sync(guild=self._guild)

                # logging
                self._logger.info(
                    f"Published {len(commands)} commands to the testing server."
                )

            # continue in production setting, dispatch commands to everyone
            case Mode.PRODUCTION:
                # syncing commands to discord
                commands = await self._tree.sync()

                # logging
                self._logger.info(f"Published {len(commands)} commands.")

    # --- getters & setters ---

    def set_mode(self, mode: Mode):
        """
        Sets the mode of the bot. This is really only applicable for when
        the bot initially launches.
        """
        if not isinstance(mode, Mode):
            raise TypeError(f"Expected type Mode, got type {type(mode)}")
        self._mode = mode

    @property
    def token(self) -> str:
        """
        Returns the token of the bot.
        """
        return self._secrets.token

    @property
    def client_id(self) -> int:
        """
        Returns the client ID of the bot.
        """
        return self._secrets.client_id

    @property
    def guild_id(self) -> int:
        """
        Returns the ID of the testing server.
        """
        return self._secrets.guild_id

    @property
    def tree(self) -> "app_commands.CommandTree[FunnyBot]":
        """
        Returns the slash command builder.
        """
        return self._tree

    # --- bot functions ---

    def terminate(self, signal, frame):
        """Gracefully terminates the bot from a synchronous context."""

        # logging
        self._logger.info(f"Received signal {signal}, shutting down bot.")

        # hooking into the event loop (need to call, async from sync func)
        loop = asyncio.get_event_loop()
        loop.create_task(self.close())

    # --- bot events ---

    async def on_ready(self):
        # setting status
        match self._mode:
            case Mode.DEVELOPMENT:
                # logging
                await self.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.playing, name="Down for maintenance."
                    ),
                    status=discord.Status.do_not_disturb,
                )

            case Mode.PRODUCTION:
                # logging
                await self.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.playing, name="iFunny Bot v2.1"
                    ),
                    status=discord.Status.online,
                )

        # logging
        self._logger.info(f"Logged in as: {self.user}")

    async def on_message(self, message: discord.message.Message):
        # guard clauses
        if message.author == self.user:  # not replying to myself
            return
        if message.author.bot:  # not replying to any messages from other bots
            return

        # debug mode shit
        if self._mode == Mode.DEVELOPMENT:
            if message.guild is None:
                return
            if message.guild.id != self.guild_id:
                return

        # testing if the interaction contains an iFunny link
        if not (urls := get_url(message.content)):
            return

        # there might be multiple urls
        for url in urls:
            # what type of url was it? post or user?
            post_type = get_datatype(url)
            match post_type:
                case PostType.USER:
                    # getting the username from the url
                    if (user := get_username_from_url(url)) is None:
                        # there was an error
                        return await message.reply(
                            content=f"Couldn't extract the username from: {url}",
                            silent=True,
                        )

                    try:
                        # making the embed
                        embed = self.get_user(user)

                        # logging
                        self._logger.info(
                            f"Replying to interaction with embed about user {user}"
                        )

                        return await message.reply(embed=embed)
                    except RuntimeError as reason:
                        # there was an error
                        return await message.reply(content=str(reason), silent=True)

                # apparently, Python won't work properly if the case is a list of enums or comma-separated
                case PostType.VIDEO | PostType.GIF | PostType.PICTURE:
                    # the post was a link to a non user
                    if not (post := get_post(url)):
                        self._logger.error(
                            f"There was an error extracting information from {message.content}"
                        )
                        await message.reply(
                            content=f"There was an internal error embedding the post from {message.content}",
                            silent=True,
                        )

                        # looping
                        continue

                    # creating an embed
                    embed = discord.Embed(
                        title=f"Post by {sanitize_special_characters(post.username)}",
                        url=post.url,
                        description=f"{post.likes} likes.\t{post.comments} comments.",
                    )
                    embed.set_author(name="", icon_url=post.icon_url)

                    # create the filename
                    filename = create_filename(post)

                    # forming the file extension
                    extension = ""
                    match post.post_type:
                        case PostType.PICTURE:
                            extension = "png"
                        case PostType.VIDEO:
                            extension = "mp4"
                        case PostType.GIF:
                            extension = "gif"
                        # this fails whenever this receives a PostType of MEME or USER
                        case _:
                            # this should never happen
                            self._logger.error(
                                f"Tried to make extension of invalid post type: {post.post_type}"
                            )

                    # creating the file object
                    file = discord.File(
                        post.content, filename=f"{filename}.{extension}"
                    )

                    # logging
                    self._logger.info(
                        f"Replying to interaction with '{filename}.{extension}'"
                    )

                    await message.reply(embed=embed, file=file)
                case _:
                    self._logger.error(
                        f"Could not discern the type of the post, silently aborting. Type was {get_datatype(url)}"
                    )
                    return None

    # --- bot functions ---

    def get_icon(self, user: str) -> "discord.File":
        """
        This function returns the target user's profile picture as a
        `discord.File` object.

        If there are any errors, a `RuntimeError`
        is raised with the reason for the failure.
        """

        # getting the user's profile
        if not (profile := get_profile_by_name(user)):
            reason = f"Could not find user {user} (although they may exist)"
            self._logger.info(reason)
            raise RuntimeError(reason)

        # getting the icon of the user
        if not (image := profile.retrieve_icon()):
            reason = f"An error occurred getting {user}'s profile picture."
            self._logger.info(reason)
            raise RuntimeError(reason)

        # user has icon, returning it
        filename = f"{profile.username}_pfp.png"
        file = discord.File(image, filename=filename)

        # logging
        self._logger.info(f"Replying to interaction with file: {filename}")

        # returning the image
        return file

    def get_user(self, user: str) -> "discord.Embed":
        """
        This function returns the target user's profile as a
        `discord.Embed` object.

        If there are any errors, a `RuntimeError`
        is raised with the reason for the failure.
        """

        # getting the user's profile
        if not (profile := get_profile_by_name(user)):
            reason = f"Could not find user '{user}' (the user might be shadow banned.)"
            self._logger.info(reason)
            raise RuntimeError(reason)

        # creating an embed for the profile
        embed = discord.Embed(description=profile.description)

        # adding info
        embed.set_author(
            name=sanitize_special_characters(profile.username), url=profile.profile_url
        )
        embed.set_thumbnail(url=profile.icon_url)
        embed.set_footer(
            text=f"{profile.subscribers} subscribers, {profile.subscriptions} subscriptions, {profile.features} features"
        )

        # logging
        self._logger.info(f"Replying to interaction with embed about: {profile}")

        # replying to interaction
        return embed

    def get_post(self, link: str) -> Tuple["discord.Embed", "discord.File"]:
        """
        This function returns the target user's post as a tuple of a `discord.Embed`
        and `discord.File` object.

        If there are any errors, a `RuntimeError` is raised with the reason for the failure.
        """

        # testing if the interaction contains an iFunny link
        if not (url := get_url(link)):
            # logging & returning
            self._logger.info(f"Received an improper link: {link}")
            raise RuntimeError(f"The url {link}, isn't a proper iFunny url.")

        # simple hack, my precious
        url = url[0]

        # got a valid link, getting the post information
        if not (post := get_post(url)):
            self._logger.error(f"There was an error extracting information from {link}")
            raise RuntimeError(
                f"There was an internal error embedding the post from {link}"
            )

        # creating an embed
        embed = discord.Embed(
            title=f"Post by {sanitize_special_characters(post.username)}",
            url=post.url,
            description=f"{post.likes} likes.\t{post.comments} comments.",
        )
        embed.set_author(name="", icon_url=post.icon_url)

        # create the filename
        filename = create_filename(post)

        # forming the file extension
        extension = ""
        match post.post_type:
            case PostType.PICTURE:
                extension = "png"
            case PostType.VIDEO:
                extension = "mp4"
            case PostType.GIF:
                extension = "gif"
            case _:
                # this should never happen
                self._logger.error(
                    f"Tried to make extension of invalid post type: {post.post_type}"
                )

        # creating the file object
        file = discord.File(post.content, filename=f"{filename}.{extension}")

        # logging
        self._logger.info(f"Replying to interaction with '{filename}.{extension}'")

        return (embed, file)
