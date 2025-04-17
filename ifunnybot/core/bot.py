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
from ifunnybot.types.post import Post
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

    def get_icon(self, user: str) -> Optional["discord.File"]:
        """
        This function returns the target user's profile picture as a
        `discord.File` object.

        If the result from this function is `None`, then the user
        doesn't have a profile picture. It is the default one.

        If there are any errors, a `RuntimeError`
        is raised with the reason for the failure.
        """

        # getting the user's profile
        if not (profile := self.get_profile_by_name(user)):
            reason = f"Could not find user '{user}' (the user might be shadow banned.)"
            self._logger.info(reason)
            raise RuntimeError(reason)

        # checking to see if this user actually has an icon
        if profile.icon_url is None:
            self._logger.info(f"User {user} doesn't have a profile picture.")
            return None

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
        embed.set_footer(
            text=f"{profile.subscribers} subscribers, {profile.subscriptions} subscriptions, {profile.features} features"
        )

        # if no icon, then don't execute this line
        if profile.icon_url is not None:
            embed.set_thumbnail(url=profile.icon_url)

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
        if not (post := self._create_post(url)):
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
        return self._create_profile(username, _headers=_headers)

    def get_profile_by_url(self, url: str, _headers=Headers) -> Optional[Profile]:
        """Get's a user's profile by url"""

        # get the username from the url
        username = get_username_from_url(url)
        if username is None:
            reason = f"Could not extract the user from {url}."
            self._logger.error(reason)
            raise LookupError(reason)

        return self._create_profile(username, _headers=_headers)

    # --- internal functions, mainly dealing with web scraping ---

    def _create_post(self, url: str, _headers=Headers) -> Optional[Post]:
        """
        This actually makes a `Profile` object by webscraping.

        If the error is something the client would want to know i.e., a user
        doesn't exist anymore. Then, a `RuntimeError` will be raised with
        the reason why. Otherwise, any failures will be returned as `None`,
        indicating some type of internal failure.
        """

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

        # what did we get from the website?
        match response.status_code:
            case _ if response.status_code > 200:
                # good
                self._logger.debug(
                    f"Received a response from the server: {response.status_code}"
                )
            case _ if response.status_code > 400:
                # post was taken down :(
                self._logger.error(
                    f"There was an error making the HTTP request to {url}"
                )
                return None
            case _ if response.status_code > 500:
                # iFunny fucked up
                self._logger.error(
                    f"Server didn't like the request, returned {response.status_code}"
                )
                return None

        # transforming the response into something useable
        dom = soup(response.text, "html.parser")
        if not dom.css:
            self._logger.fatal(
                "There was an internal error with BeautifulSoup, cannot use CSS selectors"
            )
            return None

        ## the response was OK, now scraping information
        info = Post()

        # saving the url
        info.url = url

        # pulling the data type from the url
        canonical_el = dom.css.select(Post.REAL_CONTENT_SEL[0])
        if canonical_el is None:
            self._logger.error("Couldn't find the canonical URL of the post. Aborting.")
            return None

        # grabbing the datatype
        canonical_url = canonical_el[0].get(Post.REAL_CONTENT_SEL[1], None)
        info.post_type = get_datatype(canonical_url)  # type: ignore
        if info.post_type is None:
            self._logger.error(
                f"Failed to extract datatype from canonical url: {canonical_url}"
            )
            return None

        # logging
        self._logger.info(f"Found {info.post_type.name} at {url}")

        # get the content based on the datatype
        selector, attribute = None, None
        match info.post_type:
            case PostType.PICTURE:
                (selector, attribute) = Post.PICTURE_SEL
            case PostType.VIDEO:
                (selector, attribute) = Post.VIDEO_SEL
            case PostType.GIF:
                (selector, attribute) = Post.GIF_SEL
            case _:
                self._logger.error(
                    f"Encountered bad datatype when parsing {url} was {info.post_type.name}"
                )
                return None

        # getting the element
        content_el = dom.css.select(selector)
        if content_el:
            self._logger.error(
                f"Couldn't extract the content URL from {url}, datatype was {info.post_type.name}"
            )
            return None

        # getting the content url
        info.content_url = canonical_el[0].get(attribute, None)  # type: ignore

        # checking if the content_url is not None
        if not info.content_url:
            self._logger.error(
                f"Couldn't extract the content url from {url}, datatype was {info.post_type.name}"
            )
            return None

        ## scraping other info about the post
        info.username = dom.css.select(Post.AUTHOR_SEL[0])[
            0
        ].get(Post.AUTHOR_SEL[1], default="").replace(" ", "")
        info.icon_url = dom.css.select("div._9JPE > a.WiQc > img.dLxH")[0].get(
            "data-src"
        )
        info.likes = dom.css.select("div._9JPE > button.Cgfc > span.Y2eM > span")[
            0
        ].text
        info.comments = dom.css.select("div._9JPE > button.Cgfc > span.Y2eM > span")[
            1
        ].text

        # validate the object
        info.validate()

        # logging
        self._logger.info(f"Retrieved from {url}: {info}")

        # getting the content of the post
        info.retrieve_content()

        # if the post is an image, crop it
        if info.post_type == PostType.PICTURE:
            info.crop_watermark()

        # returning the collected information
        return info

    def _create_profile(self, username: str, _headers=Headers) -> Optional[Profile]:
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
            self._logger.error(f"No such user {username} exists.")
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
