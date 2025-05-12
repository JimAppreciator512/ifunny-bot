"""
The main file for the bot.
"""

import os
import sys
import signal
import argparse
from urllib3.exceptions import NameResolutionError

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


# setup argparse
parser = argparse.ArgumentParser(description="A discord bot to embed iFunny posts.")
parser.add_argument(
    "-d",
    "--development",
    action="store_true",
    dest="dev",
    help="If flag is present, development mode is enabled. Otherwise, run in production mode.",
)
parser.add_argument(
    "-p",
    "--pickle-dir",
    default=funny.Configuration.PICKLE_LOCATION,
    dest="pickle",
    help=f"Specifies the directory (it must exist) where pickle objects are stored. Default location: {funny.Configuration.PICKLE_LOCATION}",
)
parser.add_argument(
    "-l",
    "--logs-dir",
    default=funny.Configuration.LOG_LOCATION,
    dest="logs",
    help=f"Specifies the directory (it must exist) where log files are stored. Default location: {funny.Configuration.LOG_LOCATION}",
)
parser.add_argument(
    "-f",
    "--format",
    default=funny.Configuration.IMAGE_FORMAT,
    dest="format",
    help=f"The default image export format. Default: {funny.Configuration.IMAGE_FORMAT}",
)


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

    # creating the configuration object
    conf = funny.Configuration(
        pickle_location=args.pickle, log_location=args.logs, image_format=args.format
    )

    # creating the client
    client = funny.FunnyBot(intents=intents, secrets=secrets, configuration=conf)

    # setting potential development mode
    if args.dev is True:
        client.set_mode(funny.Mode.DEVELOPMENT)

    # signal handler
    signal.signal(signal.SIGINT, lambda sig, frame: handler(sig, frame, client))
    signal.signal(signal.SIGTERM, lambda sig, frame: handler(sig, frame, client))

    # --- slash commands ---

    @client.tree.command(
        name="icon",
        description="Retrieves a user's profile picture. (case insensitive)",
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
        name="user",
        description="Embeds the link to a user's profile. (case insensitive)",
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

    @client.tree.command(
        name="post", description="Embeds a post from iFunny into Discord."
    )
    @app_commands.describe(link="An iFunny.co link e.g., ifunny.co/video/...")
    async def post(interaction: discord.Interaction, link: str):
        # deferring the reply
        await interaction.response.defer(thinking=True)

        try:
            # calling the bot
            (embed, file, content_url, actual_type) = client.get_post(link)

            # returning the image
            if client.prefer_video_url and actual_type == funny.PostType.VIDEO:
                # return await interaction.followup.send(embed=embed, content=content_url)
                return await interaction.followup.send(content=content_url)
            else:
                return await interaction.followup.send(embed=embed, file=file)
        except RuntimeError as reason:
            return await interaction.followup.send(content=str(reason), ephemeral=True)
        except NameResolutionError as reason:  # type: ignore
            return await interaction.followup.send(
                content="Encountered a DNS error, this is an known on going issue, please try again in a minute or so.",
                ephemeral=True,
            )
        except Exception as reason:  # type: ignore
            return await interaction.followup.send(
                content=f"Encounted an unexpected error: {reason}.",
                ephemeral=True,
            )

    # --- slash commands ---

    # running the bot
    client.run(secrets.token)
