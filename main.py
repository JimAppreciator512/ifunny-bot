"""
The main file for the bot.
"""

import os
import sys
import signal
import argparse

import discord
from discord import app_commands
from dotenv import dotenv_values

import ifunnybot as funny

# loading in config values
config = {**os.environ, **dotenv_values(".env")}

# getting the secrets from the environment
secrets = funny.Secrets(config)

# intents
intents = discord.Intents.default()
intents.message_content = True

# creating the client
client = funny.FunnyBot(intents=intents, secrets=secrets)


@client.tree.command(
    name="icon", description="Retrieves a user's profile picture. (case insensitive)"
)
@app_commands.rename(user_="user")
@app_commands.describe(user_="The user's name.")
async def icon(interaction: discord.Interaction, user_: str):
    # deferring the reply
    await interaction.response.defer(thinking=True)

    try:
        # calling the bot
        icon_ = client.get_icon(user_)

        # returning the image
        if icon_ is not None:
            return await interaction.followup.send(file=icon_)
        return await interaction.followup.send(
            content=f"User {user_} doesn't have a profile picture."
        )
    except RuntimeError as reason:
        return await interaction.followup.send(content=str(reason), ephemeral=True)


@client.tree.command(
    name="user", description="Embeds the link to a user's profile. (case insensitive)"
)
@app_commands.rename(user_="user")
@app_commands.describe(user_="The user's name.")
async def user(interaction: discord.Interaction, user_: str):
    # deferring the reply
    await interaction.response.defer(thinking=True)

    try:
        # calling the bot
        embed_ = client.get_user(user_)

        # passing the url as content since you actually can't click this on mobile
        url = funny.username_to_url(user_)

        # returning the image
        return await interaction.followup.send(embed=embed_, content=url)
    except RuntimeError as reason:
        return await interaction.followup.send(content=str(reason), ephemeral=True)


@client.tree.command(name="post", description="Embeds a post from iFunny into Discord.")
@app_commands.describe(link="An iFunny.co link e.g., ifunny.co/video/...")
async def post(interaction: discord.Interaction, link: str):
    # deferring the reply
    await interaction.response.defer(thinking=True)

    try:
        # calling the bot
        (embed, file) = client.get_post(link)

        # returning the image
        return await interaction.followup.send(embed=embed, file=file)
    except RuntimeError as reason:
        return await interaction.followup.send(content=str(reason), ephemeral=True)


# setup argparse
parser = argparse.ArgumentParser(description="A discord bot to embed iFunny posts.")
parser.add_argument("-d", "--development", action="store_true", dest="dev")


# signal handler
def handler(signal, frame, bot: funny.FunnyBot):
    # killing the bot
    bot.terminate(signal, frame)

    # terminating the program
    sys.exit(0)


# main loop
if __name__ == "__main__":
    # getting args
    args = parser.parse_args()

    # setting potential development mode
    if args.dev is not None:
        client.set_mode(funny.Mode.DEVELOPMENT)

    # signal handler
    signal.signal(signal.SIGINT, lambda sig, frame: handler(sig, frame, client))
    signal.signal(signal.SIGTERM, lambda sig, frame: handler(sig, frame, client))

    # running the bot
    client.run(secrets.token)
