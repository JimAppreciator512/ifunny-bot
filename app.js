// imports
import User from "./commands/user.js";
import Post from "./commands/post.js";
import Help from "./commands/help.js";
import About from "./commands/about.js";
import Config from "./commands/config.js";
import Hash from "./commands/hashfiles.js";
import DevelopmentHandler from "./env.dev.js";
import ProductionHandler from "./env.prod.js";
import { Client, GatewayIntentBits, Events } from "discord.js";
import config from "./config.json" assert { type: "json" };
import Icon from "./commands/icon.js";

// creating a list of valid commands used by the bot
const Commands = [Post, User, About, Help, Hash, Config, Icon];

// Create a new client instance
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
    ],
});

// the list of all bot commands
client.commands = Commands;

// getting all the handler functions depending on the environment
const handler = ((c) => {
    // the cleanest way I could do this
    switch (process.env.NODE_ENV) {
        case "dev":
            console.log("Running the bot in development mode.");
            return DevelopmentHandler(c);
        case "prod":
            console.log("Running the bot in production mode.");
            return ProductionHandler(c);
        default:
            console.log("No environment found, running in production mode.");
            return ProductionHandler(c);
    }
})(client);

// logging on success
client.once(Events.ClientReady, handler.ClientReady);

// regular message handler
client.on(Events.MessageCreate, handler.MessageCreate);

// slash command handler
client.on(Events.InteractionCreate, handler.InteractionCreate);

// callback loop
(async () => {
    try {
        // mapping the commands to return their "data" prop
        const payload = client.commands.map(command => {
            return command.data;
        });

        // logging the payload for debug purposes
        switch (process.env.NODE_ENV) {
            case "dev":
                console.log("Logging the payload:", payload);
                break;
            case "prod":
                break;
            default:
                break;
        }

        // logging what commands are sent to the discord API
        console.log(
            "Loading commands:",
            payload
                .map(command => {
                    return command.name;
                })
                .join(", ")
        );

        // logging
        console.log(
            `Started refreshing ${payload.length} application (/) commands.`
        );

        // The put method is used to fully refresh all commands in the guild with the current set
	try {
        	const data = await handler.Put(payload);

        	// more logging
        	console.log(
        	    `Successfully reloaded ${data.length} application (/) commands.`
        	);
	} catch (e) {
		console.error("There was an unexpected error: ", e.stack);
	}

        // logging into discord
        client.login(config.token);
    } catch (error) {
        // logging any errors
        console.error(error);
        return;
    }
})();
