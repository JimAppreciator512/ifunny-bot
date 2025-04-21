"""
This file contains the bot object.
"""

import io
import sys
import signal
import pickle
import asyncio
import hashlib
from datetime import datetime
from typing import Tuple, Optional

import pyfsig
import discord
import requests
from discord import app_commands
from bs4 import BeautifulSoup as soup
from PIL import Image, ImageOps

from ifunnybot.core.configuration import Configuration
from ifunnybot.core.logging import create_logger
from ifunnybot.types.post import Post
from ifunnybot.types.mode import Mode
from ifunnybot.types.response import Response
from ifunnybot.types.secrets import Secrets
from ifunnybot.types.profile import Profile
from ifunnybot.types.post_type import PostType
from ifunnybot.types.parsing_exception import ParsingError
from ifunnybot.data.signatures import IFUNNY_SIGS
from ifunnybot.utils.html import generate_safe_selector
from ifunnybot.utils.utils import (
    sanitize_special_characters,
    spoof_headers,
    WATERMARK_MAGIC_HASH,
)
from ifunnybot.utils.urls import (
    get_url,
    get_datatype,
    get_username_from_url,
    encode_url,
    username_to_url,
    remove_image_cropping,
)


class FunnyBot(discord.Client):
    """
    The most elite Discord bot for iFunny posts yet.
    """

    def __init__(
        self,
        *,
        intents: discord.Intents,
        secrets: Secrets,
        mode: Mode = Mode.PRODUCTION,
        log_name: str = f"{int(datetime.utcnow().timestamp())}-funnybot.log",
        configuration: Configuration = Configuration(),
    ) -> None:
        super().__init__(intents=intents)

        # saving variables
        self._logger = create_logger(f"{configuration.log_location}/{log_name}")
        self._tree = app_commands.CommandTree(
            self
        )  # the tree variable holds slash commands
        self._mode = mode
        self._headers = spoof_headers()

        # configuration
        self._log_file = log_name
        self._secrets = secrets
        self._conf = configuration
        self._guild: discord.Object = discord.Object(
            id=self._secrets.guild_id, type=discord.abc.GuildChannel
        )

    # --- setup functions ---

    async def setup_hook(self):
        # logging
        self._logger.info("Starting bot in %s mode.", self._mode.name)
        self._logger.info("Configuration object: %s", self._conf)
        self._logger.info("Secrets: %s", self._secrets)

        # wrapping around logging function
        self._manipulate_logger()

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
                    "Published %d commands to the testing server.", len(commands)
                )

            # continue in production setting, dispatch commands to everyone
            case Mode.PRODUCTION:
                # syncing commands to discord
                commands = await self._tree.sync()

                # logging
                self._logger.info("Published %d commands.", len(commands))

    # --- getters & setters ---

    @property
    def headers(self) -> dict[str, str]:
        """Returns the headers used to query iFunny"""
        return self._headers

    @property
    def pickles_dir(self) -> str:
        """Returns the directory where pickle objects are stored."""
        return self._conf.pickle_location

    @property
    def logs_dir(self) -> str:
        """Returns the directory where the logs are stored."""
        return self._conf.log_location

    @property
    def image_export_format(self) -> str:
        """Returns the default image export format used for icons and pictures."""
        return self._conf.image_format

    @property
    def log_file(self) -> str:
        """Returns the path to the currently used log file."""
        return f"{self._conf.log_location}/{self._log_file}"

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

    def _manipulate_logger(self):
        # if development mode, enable debug logs
        if self._mode == Mode.PRODUCTION:
            setattr(self._logger, "debug", lambda *args, **kwargs: str)

        # getting the original function
        original_func = getattr(self._logger, "error")

        # new wrapper
        def error(msg: object, *args: object, **kwargs) -> None:
            # calling the original logger function
            original_func(msg, *args, **kwargs)

            # logging to the error channel
            loop = asyncio.get_event_loop()
            loop.create_task(self.log_to_error_channel(msg % args))  # type: ignore

        # setting the functions
        setattr(self._logger, "error", error)
        setattr(self._logger, "_error", original_func)

    async def log_to_error_channel(self, msg: str):
        """
        This functions logs to the error channel specified by `self._secrets`.
        """
        # get the channel
        channel = self.get_channel(self._secrets.error_channel)

        # get again if channel is None
        if channel is None:
            # Fallback in case the bot hasn't cached the channel
            channel = await self.fetch_channel(self._secrets.error_channel)

        # send the message
        if isinstance(channel, discord.TextChannel):
            await channel.send(content=msg)

    def terminate(self, signum: int, _):
        """Gracefully terminates the bot from a synchronous context."""

        # logging
        self._logger.info(
            "Received signal %s(%d), shutting down bot.", signal.Signals(signum), signum
        )

        # hooking into the event loop (need to call, async from sync func)
        loop = asyncio.get_event_loop()
        loop.create_task(self.close()).add_done_callback(lambda x: sys.exit(0))

    def get_icon(self, user: str) -> Optional["discord.File"]:
        """
        This function returns the target user's profile picture as a
        `discord.File` object.

        If the result from this function is `None`, then the user
        doesn't have a profile picture. It is the default one.

        If there are any errors, a `RuntimeError`
        is raised with the reason for the failure.
        """

        # the url for errors
        url = username_to_url(user)

        # getting the user's profile
        try:
            profile = self.get_profile_by_name(user)

        # something happened
        except RuntimeError as reason:
            self._logger.error(
                "Caught RuntimeError from self._create_post(%s), was %s",
                url,
                reason,
                exc_info=True,
            )
            raise RuntimeError(
                f"There was an error made with the connection to {url}, unable to GET the website."
            ) from reason

        # some weird parsing error
        except ParsingError as reason:
            self._logger.error(
                "Caught ParsingError from self._create_post(%s), was %s",
                url,
                reason,
                exc_info=True,
            )
            raise RuntimeError(f"There was an error parsing {url}.") from reason

        # if profile is None, the user is likely shadow banned
        if profile is None:
            reason = f"Could not find user '{user}' (the user might be shadow banned.)"
            self._logger.info(reason)
            raise RuntimeError(reason)

        # checking to see if this user actually has an icon
        if profile.icon_url is None:
            self._logger.info("User %s doesn't have a profile picture.", user)
            return None

        # getting the icon of the user
        icon_response = self._retrieve_content(profile.icon_url)
        if icon_response is None:
            reason = f"An error occurred getting {user}'s profile picture."
            self._logger.error(reason)
            raise RuntimeError(reason)

        # filename
        filename = f"{profile.username}_pfp.png"

        # converting the pfp to whatever format is chosen
        converted = self._crop_convert(
            icon_response.bytes,
            force_crop=False,
            export_format=self.image_export_format,
            filename=icon_response.url,
        )

        # user has icon, returning it
        file = discord.File(converted, filename=filename)

        # logging
        self._logger.info("Replying to interaction with file: %s", filename)

        # returning the image
        return file

    def get_user(self, user: str) -> "discord.Embed":
        """
        This function returns the target user's profile as a
        `discord.Embed` object.

        If there are any errors, a `RuntimeError`
        is raised with the reason for the failure.
        """

        # the url for errors
        url = username_to_url(user)

        # getting the user's profile
        try:
            profile = self.get_profile_by_name(user)

        # something happened
        except RuntimeError as reason:
            self._logger.error(
                "Caught RuntimeError from self._create_post(%s), was %s",
                url,
                reason,
                exc_info=True,
            )
            raise RuntimeError(
                f"There was an error made with the connection to {url}, unable to GET the website."
            ) from reason

        # some weird parsing error
        except ParsingError as reason:
            self._logger.error(
                "Caught ParsingError from self._create_post(%s), was %s",
                url,
                reason,
                exc_info=True,
            )
            raise RuntimeError(f"There was an error parsing {url}.") from reason

        # if profile is None, the user is likely shadow banned
        if profile is None:
            reason = f"Could not find user '{user}' (the user might be shadow banned.)"
            self._logger.info(reason)
            raise RuntimeError(reason)

        # creating an embed for the profile
        embed = discord.Embed(description=profile.description)

        # adding info
        embed.set_author(
            name=sanitize_special_characters(profile.username), url=profile.url
        )
        embed.set_footer(
            text=f"{profile.subscribers} subscribers, {profile.subscriptions} subscriptions, {profile.features}"
        )

        # if no icon, then don't execute this line
        if profile.icon_url is not None:
            embed.set_thumbnail(url=profile.icon_url)

        # logging
        self._logger.info("Replying to interaction with embed about: %s", repr(profile))

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
            self._logger.info("Received an improper link: %s", link)
            raise RuntimeError(f"The url {link}, isn't a proper iFunny url.")

        # simple hack, my precious
        url = url[0]

        # got a valid link, getting the post information
        try:
            post = self._create_post(url, self._headers)

        # something happened
        except RuntimeError as reason:
            self._logger.error(
                "Caught RuntimeError from self._create_post(%s), was %s",
                url,
                reason,
                exc_info=True,
            )
            raise RuntimeError(
                f"There was an error made with the connection to {link}, unable to GET the website."
            ) from reason

        # some weird parsing error
        except ParsingError as reason:
            self._logger.error(
                "Caught ParsingError from self._create_post(%s), was %s",
                url,
                reason,
                exc_info=True,
            )
            raise RuntimeError(f"There was an error parsing {link}.") from reason

        # checking if the post is None, if true, then the post was taken down/shadow banned
        if post is None:
            raise RuntimeError(
                f"Couldn't embed the post at {link}. It was either taken down or incorrect."
            )

        # creating an embed
        embed = discord.Embed(
            title=f"Post by {sanitize_special_characters(post.author)}",
            url=post.url,
            description=f"{post.likes} likes.\t{post.comments} comments.",
        )
        embed.set_author(
            name=post.author,
            url=post.username_to_url(),
            icon_url=post.icon_url,
        )

        # create the filename
        filename = encode_url(post.url)

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
                    "Tried to make extension of invalid post type: %s", post.post_type
                )

        # creating the file object
        filename = f"{filename}.{extension}"
        file = discord.File(post.content, filename=filename)

        # logging
        self._logger.info("Returning object: %s", filename)

        return (embed, file)

    def get_profile_by_name(self, username: str) -> Optional[Profile]:
        """Get's a user's profile by username"""
        return self._create_profile(username, _headers=self._headers)

    def get_profile_by_url(self, url: str) -> Optional[Profile]:
        """Get's a user's profile by url"""

        # get the username from the url
        username = get_username_from_url(url)
        if username is None:
            reason = f"Could not extract the user from {url}."
            self._logger.error(reason)
            raise RuntimeError(reason)

        return self._create_profile(username, _headers=self._headers)

    # --- internal functions, mainly dealing with web scraping ---

    def _create_post(self, url: str, _headers: dict[str, str]) -> Optional[Post]:
        """
        This actually makes a `Post` object by webscraping.

        If the result is `None`, then the post doesn't exist (or the user
        is shadow banned).

        If a `ParsingError` is thrown, it means that this function failed
        to parse the website for something.

        If a `RuntimeError` is thrown, it means that something connection
        related happened.
        """

        # getting the post, assuming that it is a proper link
        response = None
        try:
            response = requests.get(
                url, headers=_headers, allow_redirects=False, timeout=10000
            )
        except Exception as e:
            reason = f"There was an exception making a GET request to {url}: {e}"
            self._logger.error(reason)
            raise RuntimeError(reason) from e

        # what did we get from the website?
        match response.status_code:
            case 200:
                self._logger.info("Found post at %s", url)
            case 404:
                self._logger.info("Post at %s was likely banned or shadow banned.", url)
                return None
            case _:
                # raising an error because something went wrong
                self._logger.error(
                    "Server responded with code %d when making request to %s, reason: %s",
                    response.status_code,
                    url,
                    response.reason,
                )
                raise RuntimeError("There was an error making the request to iFunny.")

        # transforming the response into something useable
        dom = soup(response.text, "html.parser")
        if not dom.css:
            self._logger.fatal(
                "There was an internal error with BeautifulSoup, cannot use CSS selectors"
            )
            raise ParsingError(
                "There was an internal error with BeautifulSoup, cannot use CSS selectors"
            )

        # the response was OK, now scraping information
        info = Post(url=url)

        # pulling the data type from the url
        canonical_el = dom.css.select(Post.CANONICAL_SEL[0])
        if len(canonical_el) == 0:
            # logging
            self._logger.error(
                "Couldn't obtain the canonical url of %s, aborting.", url
            )

            # pickle the webpage
            self._pickle_website(
                url,
                response.text,
                ParsingError(f"Couldn't obtain the canonical url of {url}, aborting."),
            )

            # returning
            raise ParsingError(f"Couldn't obtain the canonical url of {url}, aborting.")

        # grabbing the datatype
        canonical_url = canonical_el[0].get(Post.CANONICAL_SEL[1], None)
        info.post_type = get_datatype(canonical_url)  # type: ignore
        if info.post_type is None:
            self._logger.error(
                "Failed to extract datatype from canonical url: %s", canonical_url
            )
            raise ParsingError(
                f"Failed to extract datatype from canonical url: {canonical_url}"
            )

        # logging
        self._logger.info("Found %s at %s", info.post_type.name, url)

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
                    "Encountered bad datatype when parsing %s was %s",
                    url,
                    info.post_type.name,
                )
                raise ParsingError(
                    f"Encountered bad datatype when parsing {url} was {info.post_type.name}"
                )

        # make safe selector object
        sel = generate_safe_selector(dom)

        # if any line fails, the entire function fails, therefore,
        # this can all exist in a try/catch block
        try:
            # getting the actual content of the page
            info.content_url = sel(selector).get(attribute, None)  # type: ignore

            # getting the author
            info.author = (
                sel(Post.AUTHOR_SEL[0]).get(Post.AUTHOR_SEL[1], None).replace(" ", "")  # type: ignore
            )

            # getting the icon of the author (this can fail!)
            icon_el = dom.css.select_one(Post.ICON_SEL[0])
            if icon_el is not None:
                info.icon_url = icon_el.get(Post.ICON_SEL[1], None)  # type: ignore

            # getting the number of likes
            info.likes = sel(Post.LIKES_SEL).text

            # getting the number of comments
            info.comments = sel(Post.COMMENTS_SEL).text
        except ParsingError as reason:
            # better exception handling
            self._logger.error(
                "Failure to parse %s from %s, cannot proceed. %s",
                info.post_type.name,
                url,
                reason,
                exc_info=True,
            )

            # pickling the website as this is a parsing error
            self._pickle_website(url, response.text, reason)

            # raising the error
            raise reason
        except Exception as e:  # type: ignore
            # logging
            self._logger.error(
                "Encountered error when parsing %s: %s", url, e, exc_info=True
            )

            # pickling the website as this is a parsing error
            self._pickle_website(url, response.text, e)

            # raising
            raise e

        # logging
        self._logger.info("Retrieved from %s: %s", url, repr(info))

        # getting the content of the post
        try:
            content = self._retrieve_content(info.content_url)  # type: ignore
        except RuntimeError as reason:
            # logging
            self._logger.error(
                "Caught error from _retrieve_content(%s): %s",
                info.content_url,
                reason,
                exc_info=True,
            )

            # pickling the website as this is a parsing error
            self._pickle_website(url, response.text, reason)

            # raising
            raise RuntimeError(
                f"Error retrieving {info.post_type.name} from {url}."
            ) from reason

        # if the post is an image, crop it
        if info.post_type == PostType.PICTURE:
            content.bytes = self._crop_convert(
                content.bytes,
                force_crop=crop,
                export_format=self.image_export_format,
                filename=content.url,
            )

        # setting
        info.response = content

        # validate the object
        try:
            info.validate()
        except RuntimeError as reason:
            self._logger.error(
                "Validation of the post failed, reason: %s", reason, exc_info=True
            )
            raise reason

        # returning the collected information
        return info

    def _create_profile(
        self, username: str, _headers: dict[str, str]
    ) -> Optional[Profile]:
        """
        This actually makes a `Profile` object by webscraping.

        If the result is `None`, then the user doesn't exist (or is likely
        shadow banned).

        If a `ParsingError` is thrown, it means that this function failed
        to parse the website for something.

        If a `RuntimeError` is thrown, it means that something connection
        related happened.
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
            reason = f"There was an exception making a GET request to {url}: {e}"
            self._logger.error(reason)
            raise RuntimeError(reason) from e

        # what did we get from the website?
        match response.status_code:
            case 200:
                self._logger.info("Found user %s", username)
            case 404:
                self._logger.info("User %s doesn't exist.", username)
                return None
            case _:
                # raising an error because something went wrong
                self._logger.error(
                    "Server responded with code %d when making request to %s, reason: %s",
                    response.status_code,
                    url,
                    response.reason,
                )
                raise RuntimeError("There was an error making the request to iFunny.")

        # transforming the response into something useable
        dom = soup(response.text, "html.parser")
        if not dom.css:
            self._logger.fatal(
                "There was an internal error with BeautifulSoup, cannot use CSS selectors"
            )
            raise ParsingError(
                "There was an internal error with BeautifulSoup, cannot use CSS selectors"
            )

        ## scraping information

        # get the actual username
        if username_el := dom.css.select(Profile.USERNAME_SEL):
            profile.username = username_el[0].text.strip()
        else:
            # couldn't parse the username
            reason = f"Could't get the real username from user {username}'s profile"
            self._logger.error(reason)
            raise ParsingError(reason)

        # getting the profile picture
        if icon_el := dom.css.select(Profile.ICON_SEL):
            # the user has a pfp
            profile.icon_url = icon_el[0].get("src")  # type: ignore
        else:
            # the user does not have a pfp
            self._logger.info("User %s doesn't have a pfp.", username)

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
        self._logger.info("Retrieved from %s: %s", url, repr(profile))

        # returning the collected information
        return profile

    def _retrieve_content(self, url: str, remove_cropping: bool = True) -> Response:
        """
        Grabs the content from the iFunny CDN i.e., videos, images and gifs.

        Can throw `RuntimeError` if there was an error with the request made
        to the CDN.
        """

        # getting the post, assuming that it is a proper link
        response = None
        try:
            response = requests.get(url, allow_redirects=False, timeout=10000)
        except Exception as e:  # type: ignore
            # got an error
            self._logger.error(
                "Failed to retrieve content from %s, most likely no internet connection or a malformed url. Reason: %s",
                url,
                e,
                exc_info=True,
            )
            raise RuntimeError(
                f"Failed to retrieve content from {url}, most likely no internet connection or a malformed url. Reason: {e}"
            ) from e

        # do we have a body?
        if not response.content:
            self._logger.error(
                "Expected the response from %s to have a body, it didn't", url
            )
            raise RuntimeError(
                f"Expected the response from {url} to have a body, it didn't"
            )

        # looking at the file type from the header
        sig = None
        sigs = pyfsig.find_matches_for_file_header(
            response.content, signatures=IFUNNY_SIGS
        )

        # checking the number of signatures
        match len(sigs):
            case 0:
                self._logger.warning("pyfsig failed to determine the type of the file.")
            case 1:
                self._logger.debug("Signature of the file: %s", repr(sigs[0]))
                sig = sigs[0]
            case _:
                self._logger.warning(
                    "More than one possible signature. Total: %d; %s",
                    len(sigs),
                    ", ".join(map(lambda x: x.file_extension, sigs)),
                )
                sig = sigs[0]
                self._logger.warning(
                    "Picking the first signature: %s", sig.file_extension
                )

        # removing cropping from the CDN if specified
        _url = url
        if remove_cropping:
            _url = remove_image_cropping(_url)
            self._logger.debug("Removed cropping from the URL: %s -> %s", url, _url)

        # creating new Response object
        resp = Response(io.BytesIO(response.content), _url, sig, response)

        # logging
        self._logger.debug(resp)

        # returning the response object
        return resp

    def _crop_convert(
        self,
        _bytes: io.BytesIO,
        force_crop=False,
        export_format: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> io.BytesIO:
        """
        Converts a byte stream of type `io.BytesIO` to the specified format using PIL,
        also crops the bottom 20 pixels out of the image to remove the dreaded iFunny
        watermark.

        This function does not check whether or not `_bytes` is an actual image,
        if you try to pass in something that isn't an image, you'll most likely get an
        error.

        - `force_crop`: str - If this is true, the function will always crop the image.
        - `export_format`: Optional[str] - This dictates the output format of the image,
            this gets input directly into `Image.save(..., format=...)`
        - `filename`: Optional[str] - This is for logging, whatever string is inputted here
            will get written to the log file.
        """

        # getting the effective filename of the image
        effective_name = filename if filename is not None else "unknown"

        # turning bytes into an image
        _image = Image.open(_bytes)

        # getting format
        actual_format = export_format
        if export_format is None:
            actual_format = self._conf.image_format
            self._logger.debug(
                "Set image export format from configuration: %s", actual_format
            )

        # determining if the image should be cropped or not
        sub_image = Image.new(_image.mode, _image.size).crop(
            (_image.width - 100, _image.height - 20, _image.width, _image.height)
        )
        _hash = hashlib.sha1(sub_image.tobytes()).hexdigest()
        sub_image.close()
        should_crop = _hash == WATERMARK_MAGIC_HASH

        # new buffer
        nbuf = io.BytesIO()

        # cropping & the image
        if force_crop or should_crop:
            _image = ImageOps.crop(_image, (0, 0, 0, 20))
            self._logger.info(
                "Image from %s was cropped, had hash: %s (matches magic hash? %s)",
                effective_name,
                _hash,
                should_crop,
            )

        # logging
        self._logger.debug(
            "Image hash: %s. Should crop? %s. Forced Crop? %s. Was cropped? %s. Image name: %s",
            _hash,
            should_crop,
            force_crop,
            should_crop or force_crop,
            effective_name,
        )

        # converting the image
        _image.save(nbuf, format=actual_format)

        # logging
        # checking the file type
        if _image.format is None:
            self._logger.warning(
                "PIL could not discern what file type the image is. Converted to %s",
                actual_format,
            )
        else:
            self._logger.info("Converted %s to %s.", _image.format, actual_format)

        # cleanup
        _bytes.close()
        del _bytes
        nbuf.seek(0)

        # returning the new buffer
        return nbuf

    def _pickle_website(
        self, url: str, content: str, reason: Optional[Exception] = None
    ):
        """
        Transforms the website into a pickle file. Saves it in the following
        format:
        {
            url: `url`,
            reason: `reason`,
            payload: `content`
        }

        This should be used to debug HTML parsing errors.
        """

        # creating filename
        filename = f"{encode_url(url)}.pickle"

        # creating object
        payload = {"url": url, "reason": reason, "payload": content}

        # pickling
        with open(f"{self.pickles_dir}/{filename}", "wb") as p:
            _bytes = pickle.dumps(payload)
            p.write(_bytes)
            self._logger.info(
                "Pickled website for %s as %s/%s, %d bytes.",
                url,
                self.pickles_dir,
                filename,
                len(_bytes),
            )

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
                        type=discord.ActivityType.playing, name="iFunny Bot v2.5"
                    ),
                    status=discord.Status.online,
                )

        # logging
        self._logger.info("Logged in as: %s", repr(self.user))

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
                        await message.reply(
                            content=f"Couldn't extract the username from: {url}",
                        )
                        continue

                    try:
                        # making the embed
                        embed = self.get_user(user)

                        # logging
                        self._logger.info(
                            "Replying to interaction with embed about user %s", user
                        )

                        # passing the url as content since you actually can't click this on mobile
                        await message.reply(embed=embed, content=url)
                    except RuntimeError as reason:
                        # there was an error
                        await message.reply(content=str(reason))

                # apparently, Python won't work properly if the case is a list of enums
                # or comma-separated
                case PostType.VIDEO | PostType.GIF | PostType.PICTURE | PostType.MEME:
                    try:
                        # creating everything
                        (embed, file) = self.get_post(url)

                        # logging
                        self._logger.info(
                            "Replying to interaction with embed about post at %s", url
                        )

                        # replying to the user
                        await message.reply(embed=embed, file=file)
                    except RuntimeError as reason:
                        # there was an error
                        await message.reply(content=str(reason))

                case _:
                    self._logger.error(
                        "Could not discern the type of the post, silently aborting. Type was %s",
                        get_datatype(url),
                    )
                    return None
