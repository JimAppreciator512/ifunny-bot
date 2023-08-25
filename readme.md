# About

This is a simple bot that replies with an image or video at a specific iFunny.co link.

> [Add this bot to your server.](https://discord.com/api/oauth2/authorize?client_id=1051024538831437865&permissions=116736&scope=bot%20applications.commands)

Have any suggestions? Open an issue and I'll read it (eventually).

## Why?

I made this bot because Discord can't embed iFunny posts into channels at all and I can't save videos to iOS.
So I made this bot with this main feature in mind and a couple other features.

## Installation

> This bot can run on x86, x86-64 and arm (I've only run this on a raspberry pi 4)

This bot requires `npm` and `node.js` to run.

1. Clone the repository to your chosen location.
1. Run `npm install` to install all the packages.
1. After npm finishes, then run either `npm run dev` or `npm start` to start the bot.

You will also need your own bot token along with the bot's client ID
which means you will need to create a `config.json` file to store it.
Finally, for development purposes, you should create a private (I don't really care if it's public) server to
test the bot on.
See example below:

```json
{
	"token": "your token goes here",
	"clientId": "your application id goes here"
	"guildId": "the id of your development server goes here"
}
```

## Server Configuration

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

