// Require the necessary discord.js classes
import { REST, Routes, Client, Events, GatewayIntentBits } from "discord.js";
import config from "./config.json" assert { type: "json" };
import Ping from "./commands/ping.js";
import User from "./commands/user.js";
import About from "./commands/about.js";
import Download from "./commands/download.js";

// Create a new client instance
const client = new Client({ intents: [GatewayIntentBits.Guilds] });

// the list of all bot commands
client.commands = [Ping, Download, User, About];

// logging on success
client.once(Events.ClientReady, c => {
	console.log(`Ready! Logged in as ${c.user.tag}`);
});

// command handler, this handles the processing of commands
client.on(Events.InteractionCreate, async interaction => {
	if (!interaction.isChatInputCommand()) return;

	// filtering through the commands to find the requested command
	const [command] = client.commands.filter(command => {
		return command.data.name === interaction.commandName;
	});

	// just in case the command that was called is undefined
	if (command === undefined) {
		const msg = `You somehow tried to call an undefined command "${interaction.commandName}." Good job!`;
		console.log(msg);
		await interaction.reply({ content: msg, ephemeral: true });
		return;
	}

	// trying to execute the command
	try {
		// logging
		console.log(
			`The command ${interaction.commandName} was executed by ${interaction.member.user.username}.`
		);

		// executing the command
		await command.execute(interaction);
	} catch (error) {
		// something went wrong executing this command
		console.error(error);
		await interaction.reply({
			content: "There was an error while executing this command!",
			ephemeral: true,
		});
	}
});

// establishing a rest connection to discord
const rest = new REST({ version: "10" }).setToken(config.token);

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
		const data = await rest.put(
			Routes.applicationCommands(config.clientId),
			{ body: payload }
		);

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
