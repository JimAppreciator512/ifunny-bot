import { Events } from "discord.js";
import config from "./config.json" assert { type: "json" };
import { client, dev } from "./bootstrap.js"

// logging on success
client.once(Events.ClientReady, dev.ClientReady);

// regular message handler
client.on(Events.MessageCreate, dev.MessageCreate);

// slash command handler
client.on(Events.InteractionCreate, dev.InteractionCreate);

// deploying the commands to discord
(async () => {
	try {
		// mapping the commands to return their "data" prop
		const payload = client.commands.map(command => {
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
		client.login(config.token);
	} catch (error) {
		// logging any errors
		console.error(error);
	}
})();

