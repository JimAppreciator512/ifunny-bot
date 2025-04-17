"""
This file contains the bot object.
"""

from typing import Tuple, TYPE_CHECKING, Optional

import asyncio
import discord
import requests
from discord import app_commands
from bs4 import BeautifulSoup as soup

from ifunnybot.data.headers import Headers
from ifunnybot.core.get_post import get_post
from ifunnybot.types.mode import Mode
from ifunnybot.types.secrets import Secrets
from ifunnybot.types.profile import Profile
from ifunnybot.types.post_type import PostType
from ifunnybot.utils.utils import sanitize_special_characters, create_filename
from ifunnybot.utils.urls import (
    get_url,
    get_datatype,
    get_username_from_url,
    username_to_url,
    IFUNNY_NO_PFP,
)

if TYPE_CHECKING:
    # importing this as a type
    import logging


class FunnyBot(discord.Client):
    """
    The most elite Discord bot for iFunny posts yet.
    """

    def __init__(
        self,
        *,
        intents: discord.Intents,
        logger: "logging.Logger",
        secrets: Secrets,
        mode: Mode = Mode.PRODUCTION,
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

    def get_icon(self, user: str) -> "discord.File":
        """
        This function returns the target user's profile picture as a
        `discord.File` object.

        If there are any errors, a `RuntimeError`
        is raised with the reason for the failure.
        """

        # getting the user's profile
        if not (profile := self.get_profile_by_name(user)):
            reason = f"Could not find user {user} (although they may exist)"
            self._logger.info(reason)
            raise RuntimeError(reason)

        # checking to see if this user actually has an icon
        if profile.icon_url == IFUNNY_NO_PFP:
            reason = f"User {user} doesn't have a profile picture."
            self._logger.info(reason)
            raise RuntimeError(reason)

        # getting the icon of the user
        if not (image := profile.retrieve_icon()):
            reason = f"An error occurred getting {user}'s profile picture."
            self._logger.error(reason)
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
        if not (profile := self.get_profile_by_name(user)):
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
        embed.set_author(
            name=sanitize_special_characters(post.username),
            url=post.username_to_url(),
            icon_url=post.icon_url,
        )

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

    def get_profile_by_name(self, username: str, _headers=Headers) -> Optional[Profile]:
        """Get's a user's profile by username"""
        return self._get_profile(username, _headers=_headers)

    def get_profile_by_url(self, url: str, _headers=Headers) -> Optional[Profile]:
        """Get's a user's profile by url"""

        # get the username from the url
        username = get_username_from_url(url)
        if username is None:
            reason = f"Could not extract the user from {url}."
            self._logger.error(reason)
            raise LookupError(reason)

        return self._get_profile(username, _headers=_headers)

    def _get_profile(self, username: str, _headers=Headers) -> Optional[Profile]:
        """
        This actually makes a `Profile` object by webscraping.

        If the error is something the client would want to know i.e., a user
        doesn't exist anymore. Then, a `RuntimeError` will be raised with
        the reason why. Otherwise, any failures will be returned as `None`,
        indicating some type of internal failure.
        """

        # creating the url of the user
        url = username_to_url(username)

        # creating the profile object
        profile = Profile(username=username)

        # getting the post, assuming that it is a proper link
        response = None
        try:
            response = requests.get(
                url, headers=_headers, allow_redirects=False, timeout=10000
            )
        except Exception as e:
            self._logger.error(
                f"There was an exception making a GET request to {url}: {e}"
            )
            return None

        # testing the response code
        if response.status_code != 200:
            # do something here
            self._logger.error(f"No such user at {url} exists.")
            return None

        # transforming the response into something useable
        dom = soup(response.text, "html.parser")
        if not dom.css:
            self._logger.fatal(
                "There was an internal error with BeautifulSoup, cannot use CSS selectors"
            )
            return None

        ## scraping information

        # get the actual username
        if username_el := dom.css.select(Profile.USERNAME_SEL):
            # the user has a pfp
            profile.username = username_el[0].text.strip()
        else:
            # the user does not have a pfp
            self._logger.error(
                f"Could't get the real username from user {username}'s profile"
            )

        # getting the profile picture
        if icon_el := dom.css.select(Profile.ICON_SEL):
            # the user has a pfp
            profile.icon_url = icon_el[0].get("src")  # type: ignore
        else:
            # the user does not have a pfp
            self._logger.info(f"User {username} doesn't have a pfp.")

        # getting the description
        if description_el := dom.css.select(Profile.DESCRIPTION_SEL):
            # the user has a description
            profile.description = description_el[0].text.strip()
        else:
            profile.description = "No description."

        # getting the subscriber count
        if subscriber_el := dom.css.select(Profile.SUBSCRIBERS_SEL):
            profile.subscribers = subscriber_el[0].text.strip().split(" ")[0]
        else:
            profile.subscribers = "No subscribers."

        # getting the subscriptions
        if subscription_el := dom.css.select(Profile.SUBSCRIPTIONS_SEL):
            profile.subscriptions = subscription_el[0].text.strip().split(" ")[0]
        else:
            profile.subscriptions = "No subscriptions."

        # getting the features
        if features_el := dom.css.select(Profile.FEATURES_SEL):
            profile.features = features_el[0].text.strip().split(" ")[0]
        else:
            profile.features = "No features."

        # logging
        self._logger.info(f"Retrieved from {url}: {profile}")

        # returning the collected information
        return profile

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
                case PostType.VIDEO | PostType.GIF | PostType.PICTURE | PostType.MEME:
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
