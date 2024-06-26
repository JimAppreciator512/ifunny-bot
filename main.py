"""
The main file for the bot.
"""

import os
import sys

import discord
from discord import app_commands
from dotenv import dotenv_values

import ifunnybot as funny
from ifunnybot.core import Logger, FunnyBot
from ifunnybot.utils import sanitize_discord, create_filename

# loading in config values
config = {
    **os.environ,
    **dotenv_values(".env")
}

# vars
DEV_MODE = False
DEV_SERVER = 0

# checking the .env values
Logger.debug("Checking for DEV to be set, if so, start in development mode.")
try:
    DEV_MODE = bool(config["DEV"])
    Logger.debug("DEV is set, starting in development mode.")
except:
    Logger.debug("DEV not set, starting in production.")


# development mode checks
if DEV_MODE:
    # checking for the development server id
    if not config["GUILDID"]:
        Logger.warn(f"The bot is currently running in development mode but the ID of the development server is not set, development mode won't work correctly.")
    else:
        # checking if the development server is an integer (it should be)
        try:
            DEV_SERVER = int(config["GUILDID"])
        except Exception:
            Logger.fatal("Could not cast GUILDID to an integer, development mode won't work correctly.")


# checking for the token
Logger.debug("Checking for TOKEN...")
if not config["TOKEN"]:
    Logger.fatal("Couldn't start bot, missing 'TOKEN' from .env values.")
    sys.exit(1)
Logger.debug("TOKEN is set.")


# intents
intents = discord.Intents.default()
intents.message_content = True

# creating the client
client = FunnyBot(intents=intents, logger=Logger, guildId=DEV_SERVER)


@client.event
async def on_ready():
    Logger.info(f"Logged in as: '{client.user}'")

    # presence message
    _status, _tag = None, None
    if DEV_MODE:
        # development mode
        _status = discord.Status.do_not_disturb
        _tag = "Down for maintenance."
    else:
        # production
        _status = discord.Status.online
        _tag = "iFunny Bot v2.0"

    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=_tag), status=_status)


@client.event
async def on_message(message: discord.message.Message):
    # guard clauses
    if message.author == client.user: # not replying to myself
        return
    if message.author.bot: # not replying to any messages from other bots
        return
    if not message.guild: # the message didn't come from a server
        return
    
    # debug mode shit
    if DEV_MODE:
        if message.guild.id != int(config["GUILDID"]):
            # ignoring commands when in development mode
            return

    # ignoring messages that do not have an ifunny link
    if not funny.has_url(message.content):
        return
    
    # testing if the interaction contains an iFunny link
    if not (urls := funny.get_url(message.content)):
        return

    # there might be multiple urls
    for url in urls:
        # what type of url was it? post or user?
        t = funny.get_datatype(url)
        print(url, t, type(t))
        match t:
            case funny.PostType.USER:
                # embed a user post
                if not (profile := funny.get_profile_by_url(url)):
                    Logger.info(f"Could not find user '{user}' (although they may exist)")
                    return
                else:
                    # creating an embed for the profile
                    embed = discord.Embed(description=profile.description)

                    # adding info
                    embed.set_author(name=sanitize_discord(profile.username),
                                     url=profile.profile_url)
                    embed.set_thumbnail(url=profile.icon_url)
                    embed.set_footer(text=f"{profile.subscribers} subscribers, {profile.subscriptions} subscriptions, {profile.features} features")

                    # logging
                    Logger.info(f"Replying to interaction with embed about: {profile}")

                    # replying to interaction
                    return await message.reply(embed=embed)

            # apparently, Python won't work properly if the case is a list of enums or comma-separated
            case funny.PostType.VIDEO | funny.PostType.GIF | funny.PostType.PICTURE:
                # the post was a link to a non user
                if not (post := funny.get_post(url)):
                    Logger.error(f"There was an error extracting information from {message.content}")
                    await message.reply(content=f"There was an internal error embedding the post from {message.content}", silent=True)

                    # looping
                    continue
    
                # creating an embed
                embed = discord.Embed(title=f"Post by {sanitize_discord(post.username)}",
                                      url=post.url,
                                      description=f"{post.likes} likes.\t{post.comments} comments.")
                embed.set_author(name="", icon_url=post.icon_url)

                # create the filename
                filename = create_filename(post)
    
                # forming the file extension
                extension = ""
                match post.post_type:
                    case funny.PostType.PICTURE:
                        extension = "png"
                    case funny.PostType.VIDEO:
                        extension = "mp4"
                    case funny.PostType.GIF:
                        extension = "gif"
                    case _:
                        # this should never happen
                        Logger.error(f"Tried to make extension of invalid post type: {post.post_type}")
    
                # creating the file object
                file = discord.File(post.content, filename=f"{filename}.{extension}")
    
                # logging
                Logger.info(f"Replying to interaction with '{filename}.{extension}'")
                    
                await message.reply(embed=embed, file=file)
            case _:
                Logger.error(f"Could not discern the type of the post, silently aborting. Type was {funny.get_datatype(url)}")
                return None


@client.tree.command(name="icon", description="Retrieves a user's profile picture. (case insensitive)")
@app_commands.describe(user="The user's name.")
async def icon(interaction: discord.Interaction, user: str):    
    # deferring the reply
    await interaction.response.defer(thinking=True)

    # getting the user's profile
    if not (profile := funny.get_profile_by_name(user)):
        Logger.info(f"Could not find user '{user}' (although they may exist)")
        return await interaction.followup.send(content=f"Could not find user '{user}' (although they may exist)")
    else:
        # getting the icon of the user
        if not (image := profile.retrieve_icon()):
            Logger.info(f"An error occurred getting '{user}'s profile picture.")
            return await interaction.followup.send(content=f"An error occurred getting '{user}'s profile picture.")

        # user has icon, returning it
        file = discord.File(image, filename=f"{profile.username}_pfp.png")

        # logging
        Logger.info(f"Replying to interaction with file: {profile.username}_pfp.png")

        # returning the image
        return await interaction.followup.send(file=file)


@client.tree.command(name="user", description="Embeds the link to a user's profile. (case insensitive)")
@app_commands.describe(user="The user's name.")
async def user(interaction: discord.Interaction, user: str):    
    # deferring the reply
    await interaction.response.defer(thinking=True)

    # getting the user's profile
    if not (profile := funny.get_profile_by_name(user)):
        Logger.info(f"Could not find user '{user}' (although they may exist)")
        return await interaction.followup.send(content=f"Could not find user '{user}' (although they may exist)")
    else:
        # creating an embed for the profile
        embed = discord.Embed(description=profile.description)

        # adding info
        embed.set_author(name=sanitize_discord(profile.username),
                         url=profile.profile_url)
        embed.set_thumbnail(url=profile.icon_url)
        embed.set_footer(text=f"{profile.subscribers} subscribers, {profile.subscriptions} subscriptions, {profile.features} features")

        # logging
        Logger.info(f"Replying to interaction with embed about: {profile}")

        # replying to interaction
        return await interaction.followup.send(embed=embed)
    

@client.tree.command(name="post", description="Posts a video/image from iFunny.")
@app_commands.describe(link="An iFunny.co link e.g., ifunny.co/video/...")
async def post(interaction: discord.Interaction, link: str):
    # deferring the reply
    await interaction.response.defer(thinking=True)

    # testing if the interaction contains an iFunny link
    if not (url := funny.get_url(link)):
        # logging & returning
        Logger.info(f"Received an improper link: {link}")
        return await interaction.followup.send(content=f"The url {link}, isn't a proper iFunny url.")
    
    # simple hack, my precious
    url = url[0]

    # got a valid link, getting the post information
    if not (post := funny.get_post(url)):
        Logger.error(f"There was an error extracting information from {link}")
        return await interaction.followup.send(content=f"There was an internal error embedding the post from {link}")

    # creating an embed
    embed = discord.Embed(title=f"Post by {sanitize_discord(post.username)}",
                          url=post.url,
                          description=f"{post.likes} likes.\t{post.comments} comments.")
    embed.set_author(name="", icon_url=post.icon_url)

    # create the filename
    filename = create_filename(post)

    # forming the file extension
    extension = ""
    match post.post_type:
        case funny.PostType.PICTURE:
            extension = "png"
        case funny.PostType.VIDEO:
            extension = "mp4"
        case funny.PostType.GIF:
            extension = "gif"
        case _:
            # this should never happen
            Logger.error(f"Tried to make extension of invalid post type: {post.post_type}")

    # creating the file object
    file = discord.File(post.content, filename=f"{filename}.{extension}")

    # logging
    Logger.info(f"Replying to interaction with '{filename}.{extension}'")
        
    return await interaction.followup.send(embed=embed, file=file)


# main loop
client.run(config["TOKEN"])

