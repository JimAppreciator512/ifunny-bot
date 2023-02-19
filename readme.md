# About

This is a simple bot that replies with an image or video at a specific iFunny.co link.

>[Add this bot to your server.](https://discord.com/api/oauth2/authorize?client_id=1051024538831437865&permissions=116736&scope=bot%20applications.commands)

## Why?

Because iFunny.co links don't embed into discord properly, this bot will go to the iFunny.co link, find the `src` tag and reply with the url
that is associated with that specific image or video.

## Installation

This bot requires `npm` and `node.js` to run.

1. Clone the repository to your chosen location.
1. Run `npm install` to install all the packages.
1. After npm finishes, then run either `npm run dev` or `npm start` to start the bot.

You will also need your own bot token along with the bot's client ID which means you will need to create a `config.json` file to store it.
See example below:

```json
{
	"token": "your token goes here",
	"clientId": "your application id goes here"
}
```

