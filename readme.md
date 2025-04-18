# About

This is a simple bot that replies with an image or video at a specific iFunny.co link.
The reason why this was made is because iFunny URLs aren't properly embedded into discord and there's no way to download videos on iOS.

>[Add this bot to your server.](https://discord.com/api/oauth2/authorize?client_id=1051024538831437865&permissions=116736&scope=bot%20applications.commands)

Have any suggestions? Open an issue and I'll read it (eventually).

## Installation

>This bot can run on x86, x86-64 and arm (I've only run this on a raspberry pi 4)

This bot was written in Python and can be containerized in Docker.
Be sure to run the `setup.sh` file to create and install all the required files, except for the `.env` file.

## Commands

The following commands are currently supported:

- `/post` - embeds a post such as `https://ifunny.co/picture/EPTuXACKC?s=cl` into discord
- `/user` - embeds a user's profile, e.g., `https://ifunny.co/user/lFunnyComments`
- `/icon` - gets a user's profile picture (or icon)

The bot will automatically embed any urls it sees that have `ifunny.co` in them.

### Future Commands

- `/subscriptions` - sends a list of a user's subscriptions
- `/subscribers` - sends a list of a user's subscribers
- `/banner` - gets a user's banner
- `/config` - configures the bot for the current server

I'm open to suggestions.

## Bot Configuration

You will also need your own bot token which means you will need to create a `.env` file to store it.
Finally, for development purposes, you should create a private (I don't really care if it's public) server to test the bot on.

See example below:

```env
TOKEN=YOUR_BOT_TOKEN (required)
CLIENTID=your_bots_client_id_here (required)
GUILDID=YOUR_DEV_SERVER_ID_HERE (required)
ERRORCHANNEL=id_of_some_channel_here (required)
```

The `.env` file should reside in the same folder as `main.py`.
All secrets are stored in the `Secrets` object at run time.

### Logging

The bot logs all of its events into a log file created within the `FunnyBot` class.
All logs are saved into the `logs/` directory.

You can change this behavior using the `-l <dir>` flag.

The bot logs errors to the log file and to the channel ID specified by `ERRORCHANNEL`. See implementation below:

```py
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
```

### Pickles

Whenever there's an error during parsing, the website gets *pickled* and saved into (by default) the `pickles/` directory.

You can change this behavior using the `-p <dir>` flag.

### Image Export Format

## Docker

I've created a Docker build file to containerize the bot because logging was a fucking pain in the ass to manage on my host machine.
Also, it's better to have your services containerized so they don't interfere with the other processes running on the machine, also packages.

To have your logs written to the host machine from the image, this is my docker compose file from my machine:

```yml
services:
  funnybot:
    container_name: "funnybot"
    build: /path/to/cloned/dir
    volumes:
      - /path/to/your/logs/dir:/app/logs/
      - /path/to/your/pickles/dir:/app/pickles/
```

## Server Configuration

>This is currently not implemented.

There are several commands to control how the bot behaves on your server:

>Note that all of the `/config` subcommands require either "administrator" or "manage server" to be used.

- `/config autoembed`
  - this is true by default, whenever a message contains a link to a post on iFunny the bot will automatically embed it in the channel, this is any channel on the server that the bot has access to
  - when set to false, it will only autoembed in the channels set by `/config channels`
- `/config channels`
  - when `autoembed` is set to false, the bot will look at the list of channels saved, if a message that has an ifunny link is posted in any of these saved channels, the bot will autoembed the post
  - the bot must have access to any channel that you save
- `/config role`
  - this sets a role that can configure the bot
  - by default, anyone with the "administrator" or "manage server" permission can use this command
- `/config file-format`
  - this sets the default image export format of all the image posts that are embedded by the bot
  - by default this is set to "png" with support for:
    - "png"
    - "heif"
    - and more to come

If the bot has an error pulling information about your server at any time, there is likely an issue with the database running in production. In this case the bot should behave as normal without any configuration settings.

>To be honest I don't really expect anyone to turn off the `autoembed` feature, but it's there if you want or need it.
