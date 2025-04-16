"""
This file contains the bot object.
"""

import logging

import discord
from discord import app_commands

from ifunnybot.core.logging import Logger
from ifunnybot.core.get_profile import get_profile_by_name, get_username_from_url, get_profile_by_url
from ifunnybot.core.get_post import get_post
from ifunnybot.types.mode import Mode
from ifunnybot.types.secrets import Secrets
from ifunnybot.types.post_type import PostType
from ifunnybot.utils.urls import get_url, get_datatype
from ifunnybot.utils.utils import sanitize_special_characters, create_filename


class FunnyBot(discord.Client):
    def __init__(
        self, *,
        intents: discord.Intents,
        logger: logging.Logger,
        secrets: Secrets
    ) -> None:
        super().__init__(intents=intents)

        # saving variables
        self._logger = logger # saving the reference to the logger
        self._tree = app_commands.CommandTree(self) # the tree variable holds slash commands
        self._mode: Mode = Mode.PRODUCTION
        self._secrets = secrets
        self._guild: discord.Object = None # type: ignore

    # --- setup functions ---

    async def setup_hook(self):
        # logging
        self._logger.info("Starting bot in %s mode." % self._mode.name)

        # publishing commands
        match self._mode:
            # if in development, dispatch commands to our testing server
            case Mode.DEVELOPMENT:
                # create a reference to our guild
                self._guild = discord.Object(id=self._secrets.guild_id, type=discord.abc.GuildChannel)

                # dispatching
                self._tree.copy_global_to(guild=self._guild)

                # logging
                self._logger.debug(f"Copied commands to development server.")

            # continue in production setting
            case Mode.PRODUCTION:
                # syncing commands to discord
                commands = await self._tree.sync()

                # logging
                self._logger.info("Published %d commands." % (len(commands)))

    # --- getters & setters ---

    @property
    def token(self) -> str:
        return self._secrets.token
    
    @property
    def client_id(self) -> int:
        return self._secrets.client_id
    
    @property
    def guild_id(self) -> int:
        return self._secrets.guild_id

    @property
    def tree(self) -> "app_commands.CommandTree[FunnyBot]":
        return self._tree

    # --- bot commands ---

    async def on_ready(self):
        # setting status
        match self._mode:
            case Mode.DEVELOPMENT:
                # logging
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,
                    name="Down for maintenance."), status=discord.Status.do_not_disturb)

            case Mode.PRODUCTION:
                # logging
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,
                    name="iFunny Bot v2.1"), status=discord.Status.online)


        # logging
        Logger.info(f"Logged in as: {self.user}")

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
                    user = get_username_from_url(url)

                    # embed a user post
                    if not (profile := get_profile_by_url(url)):
                        Logger.info(f"Could not find user '{user}' (although they may exist)")
                        return
                    
                    # creating an embed for the profile
                    embed = discord.Embed(description=profile.description)

                    # adding info
                    embed.set_author(name=sanitize_special_characters(profile.username),
                                    url=profile.profile_url)
                    embed.set_thumbnail(url=profile.icon_url)
                    embed.set_footer(text=f"{profile.subscribers} subscribers, {profile.subscriptions} subscriptions, {profile.features} features")

                    # logging
                    Logger.info(
                        f"Replying to interaction with embed about: {profile}")

                    # replying to interaction
                    return await message.reply(embed=embed)

                # apparently, Python won't work properly if the case is a list of enums or comma-separated
                case PostType.VIDEO | PostType.GIF | PostType.PICTURE:
                    # the post was a link to a non user
                    if not (post := get_post(url)):
                        Logger.error(f"There was an error extracting information from {
                                    message.content}")
                        await message.reply(content=f"There was an internal error embedding the post from {message.content}", silent=True)

                        # looping
                        continue

                    # creating an embed
                    embed = discord.Embed(title=f"Post by {sanitize_special_characters(post.username)}",
                                        url=post.url,
                                        description=f"{post.likes} likes.\t{post.comments} comments.")
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
                            Logger.error(f"Tried to make extension of invalid post type: {
                                        post.post_type}")

                    # creating the file object
                    file = discord.File(post.content, filename=f"{
                                        filename}.{extension}")

                    # logging
                    Logger.info(f"Replying to interaction with '{
                                filename}.{extension}'")

                    await message.reply(embed=embed, file=file)
                case _:
                    Logger.error(f"Could not discern the type of the post, silently aborting. Type was {
                                get_datatype(url)}")
                    return None


    async def get_icon(self, interaction: discord.Interaction, user: str):
        # deferring the reply
        await interaction.response.defer(thinking=True)

        # getting the user's profile
        if not (profile := get_profile_by_name(user)):
            Logger.info(f"Could not find user '{user}' (although they may exist)")
            return await interaction.followup.send(content=f"Could not find user '{user}' (although they may exist)")
        else:
            # getting the icon of the user
            if not (image := profile.retrieve_icon()):
                Logger.info(f"An error occurred getting '{
                            user}'s profile picture.")
                return await interaction.followup.send(content=f"An error occurred getting '{user}'s profile picture.")

            # user has icon, returning it
            file = discord.File(image, filename=f"{profile.username}_pfp.png")

            # logging
            Logger.info(f"Replying to interaction with file: {profile.username}_pfp.png")

            # returning the image
            return await interaction.followup.send(file=file)


    async def get_user(self, interaction: discord.Interaction, user: str):
        # deferring the reply
        await interaction.response.defer(thinking=True)

        # getting the user's profile
        if not (profile := get_profile_by_name(user)):
            Logger.info(f"Could not find user '{user}' (although they may exist)")
            return await interaction.followup.send(content=f"Could not find user '{user}' (although they may exist)")
        else:
            # creating an embed for the profile
            embed = discord.Embed(description=profile.description)

            # adding info
            embed.set_author(name=sanitize_special_characters(profile.username),
                            url=profile.profile_url)
            embed.set_thumbnail(url=profile.icon_url)
            embed.set_footer(text=f"{profile.subscribers} subscribers, {
                            profile.subscriptions} subscriptions, {profile.features} features")

            # logging
            Logger.info(f"Replying to interaction with embed about: {profile}")

            # replying to interaction
            return await interaction.followup.send(embed=embed)


    async def get_post(self, interaction: discord.Interaction, link: str):
        # deferring the reply
        await interaction.response.defer(thinking=True)

        # testing if the interaction contains an iFunny link
        if not (url := get_url(link)):
            # logging & returning
            Logger.info(f"Received an improper link: {link}")
            return await interaction.followup.send(content=f"The url {link}, isn't a proper iFunny url.")

        # simple hack, my precious
        url = url[0]

        # got a valid link, getting the post information
        if not (post := get_post(url)):
            Logger.error(f"There was an error extracting information from {link}")
            return await interaction.followup.send(content=f"There was an internal error embedding the post from {link}")

        # creating an embed
        embed = discord.Embed(title=f"Post by {sanitize_special_characters(post.username)}",
                            url=post.url,
                            description=f"{post.likes} likes.\t{post.comments} comments.")
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
                Logger.error(f"Tried to make extension of invalid post type: {
                            post.post_type}")

        # creating the file object
        file = discord.File(post.content, filename=f"{filename}.{extension}")

        # logging
        Logger.info(f"Replying to interaction with '{filename}.{extension}'")

        return await interaction.followup.send(embed=embed, file=file)
