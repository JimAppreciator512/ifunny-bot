// Require the necessary discord.js classes
import { REST, Routes, Client, Events, GatewayIntentBits } from "discord.js";
import config from "./config.json" assert { type: "json" };
import Ping from "./commands/ping.js";
import Download from "./commands/download.js";

// Create a new client instance
const client = new Client({ intents: [GatewayIntentBits.Guilds] });

// the list of all bot commands
client.commands = [
	Ping,
	Download
];

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

	// trying to execute the command
	try {
		// logging
		console.log(`The command ${interaction.commandName} was executed by ${interaction.member.user.username}.`);

		// executing the command
		await command.execute(interaction);
	} catch (error) {
		// something went wrong executing this command
		console.error(error);
		await interaction.reply({ content: "There was an error while executing this command!", ephemeral: true });
	}
});

// establishing a rest connection to discord
const rest = new REST({ version: '10' }).setToken(config.token);

// deploying the commands to discord
(async () => {
	try {
		const payload = client.commands.map(command => {
			return command.data;
		});

		console.log(payload);

		console.log("Loading commands:", payload.map(command => {
			return command.name;
		}).join(", "));

		console.log(`Started refreshing ${payload.length} application (/) commands.`);

		// The put method is used to fully refresh all commands in the guild with the current set
		const data = await rest.put(
			Routes.applicationCommands(config.clientId),
			{ body: payload },
		);

		console.log(`Successfully reloaded ${data.length} application (/) commands.`);

		// logging into discord
		client.login(config.token);
	} catch (error) {
		// And of course, make sure you catch and log any errors!
		console.error(error);
	}
})();
