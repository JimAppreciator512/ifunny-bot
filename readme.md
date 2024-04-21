# About

This is a simple bot that replies with an image or video at a specific iFunny.co link.

>[Add this bot to your server.](https://discord.com/api/oauth2/authorize?client_id=1051024538831437865&permissions=116736&scope=bot%20applications.commands)

Have any suggestions? Open an issue and I'll read it (eventually).

## Why?

I made this bot because Discord can't embed iFunny posts into channels at all and I can't save videos to iOS.
So I made this bot with this main feature in mind and a couple other features.

## Installation

>This bot can run on x86, x86-64 and arm (I've only run this on a raspberry pi 4)

This bot was written in Python and can be containerized in Docker.
Be sure to run the `setup.sh` file to create and install all the required files (except for `.env` and `headers.pickle`).

Important file structure:

```
.../
    ifunnybot/
    .dockerignore/
    ...
    .env
    headers.pickle
    main.py
    ...
```

### Bot Configuration (`.env`)

You will also need your own bot token which means you will need to create a `.env` file to store it.
Finally, for development purposes, you should create a private (I don't really care if it's public) server to
test the bot on.
See example below:

```env
TOKEN=YOUR_BOT_TOKEN
GUILID=YOUR_DEV_SERVER_ID_HERE
```

>This magical `.env` should live in the same directory as everything else in the project.
>Also, in the Python rewrite (the current code) `CLIENDID` is never actually used, I'm not sure why.

### HTTP Requests (`headers.pickle`)

In order for iFunny to not reject the HTTP requests from the bot, you **must** spoof your headers i.e., copy
the headers made to some random website and convert them into a python-dictionary format and then
use the `pickle` module to dump them into a file called `headers.pickle`.

>I haven't included my own headers as they are personal information about me, I'll investigate what headers are strictly required.
>This requirement might also change depending on how the iFunny API behaves.

### Logging (`logs/`)

This bot logs quite a lot, but nothing that's personal. The bot will log to the current working directory + `/logs/`.

>This bot will fail if the directory doesn't exist, something I should probably fix.

### Docker

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
    networks:
      - your_network_here
```

## Server Configuration (CURRENTLY UNIMPLEMENTED IN THE LIVE REWRITE)

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

