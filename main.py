"""
The main file for the bot.
"""

import logging
import sys

import ifunnybot

import discord
from discord import app_commands
from dotenv import dotenv_values

# loading in config values
config = {
    **dotenv_values(".env")
}

# intents
intents = discord.Intents.default()
intents.message_content = True

# creating a logger
logger = logging.getLogger("FunnyBot")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

# creating the client
client = ifunnybot.FunnyBot(intents=intents, logger=logger, guildId=config["GUILDID"])

@client.event
async def on_ready():
    logger.info(f"Logged in as: '{client.user}'")

@client.event
async def on_message(message):
    # guard clauses
    if message.author == client.user:
        return
    if message.bot:
        return

@client.tree.command()
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Ping, {interaction.user.mention}")


# main loop
#client.run(config["TOKEN"])

