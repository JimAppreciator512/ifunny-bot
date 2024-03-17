"""
The main file for the bot.
"""

import io

import discord
from discord import File, app_commands
from PIL import Image
from dotenv import dotenv_values

import ifunnybot as funny
from ifunnybot.core import Logger, FunnyBot
from ifunnybot.types import PostType
from ifunnybot.utils import crop_watermark, sanitize_discord

# loading in config values
config = {
    **dotenv_values(".env")
}

# intents
intents = discord.Intents.default()
intents.message_content = True

# creating the client
client = FunnyBot(intents=intents, logger=Logger, guildId=config["GUILDID"])

@client.event
async def on_ready():
    Logger.info(f"Logged in as: '{client.user}'")

@client.event
async def on_message(message: discord.message.Message):
    # guard clauses
    if message.author == client.user:
        return
    if message.author.bot:
        return

@client.tree.command(name="post", description="Posts a video/image from iFunny.")
@app_commands.describe(link="An iFunny.co link e.g., ifunny.co/video/...")
async def post(interaction: discord.Interaction, link: str):
    # deferring the reply
    await interaction.response.defer(thinking=True)

    # testing if the interaction contains an iFunny link
    if not (url := funny.get_url(link)):
        Logger.info("Received an improper link: {link}")
        return await interaction.followup.send(content=f"The url {link}, isn't a proper iFunny url.")
    
    # got a valid link, getting the post information
    if not (post := funny.get_post(url)):
        Logger.error("There was an error extracting information from {link}")
        return await interaction.followup.send(content=f"There was an internal error embedding the post from {link}")

    # creating an embed
    embed = discord.Embed(title=f"Post by {sanitize_discord(post.username)}",
                          url=post.url,
                          description=f"{post.likes} likes.\t{post.comments} comments.")
    embed.set_author(name="", icon_url=post.icon_url)

    # if the post is an image, get and crop the image specified
    if post.post_type == PostType.PICTURE:
        if not (image := crop_watermark(post)):
            Logger.error("There was an error cropping the image.")
            return await interaction.followup.send(content="There was an error cropping the image")

        # setting the file content
        byte_arr = io.BytesIO()
        image.save(byte_arr, format="PNG")
        byte_arr.seek(0) # apparently, this just fixes everything

        # creating the File object
        file = discord.File(byte_arr, filename="test.png")
    
        # getting the url from the content
        return await interaction.followup.send(embed=embed, file=file)
    else:
        # creating file content from a video or a gif
        return await interaction.followup.send(embed=embed, content=post.content_url)

# main loop
client.run(config["TOKEN"])

