# About

This is a simple bot that replies with an image or video at a specific iFunny.co link.

> [Add this bot to your server.](https://discord.com/api/oauth2/authorize?client_id=1051024538831437865&permissions=116736&scope=bot%20applications.commands)

## Why?

I made this bot because Discord can't embed iFunny posts into channels at all and I can't save videos to iOS.
So I made this bot with this main feature in mind and a couple other features.

## Installation

> This bot can run on x86-64 and arm (I've only run this on a raspberry pi 4)

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
