import { Events } from "discord.js";
import config from "./config.json" assert { type: "json" };
import { Client, dev } from "./bootstrap.js"

// logging on success
Client.once(Events.ClientReady, dev.ClientReady);

// regular message handler
Client.on(Events.MessageCreate, dev.MessageCreate);

// slash command handler
Client.on(Events.InteractionCreate, dev.InteractionCreate);

// deploying the commands to discord
(async () => {
	try {
		// mapping the commands to return their "data" prop
		const payload = Client.commands.map(command => {
			return command.data;
		});

		// for debug purposes
		console.log(payload);

		// logging what commands are sent to the discord API
		console.log(
			"Loading commands:",
			payload
				.map(command => {
					return command.name;
				})
				.join(", ")
		);

		console.log(
			`Started refreshing ${payload.length} application (/) commands.`
		);

		// The put method is used to fully refresh all commands in the guild with the current set
		const data = await dev.Put(payload);

		console.log(
			`Successfully reloaded ${data.length} application (/) commands.`
		);

		// logging into discord
		Client.login(config.token);
	} catch (error) {
		// logging any errors
		console.error(error);
	}
})();

