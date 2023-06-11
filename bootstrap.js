// Require the necessary discord.js classes
import { REST, Routes, Client, GatewayIntentBits } from "discord.js";
import config from "./config.json" assert { type: "json" };
import User from "./commands/user.js";
import About from "./commands/about.js";
import Download from "./commands/download.js";
import { isValidiFunnyLink } from "./utils/utils.js";
import extractPost from "./utils/extractpost.js";

// Create a new client instance
const client = new Client({ intents: [
	GatewayIntentBits.Guilds,
	GatewayIntentBits.GuildMessages,
	GatewayIntentBits.MessageContent
] });

// the list of all bot commands
client.commands = [Download, User, About];

// establishing a rest connection to discord
const rest = new REST({ version: "10" }).setToken(config.token);

const dev = {
	ClientReady: c => {
		console.log(`Ready! Logged in as ${c.user.tag}`);

		// for maintenance
		client.user.setActivity("Down for maintenance!");
		client.user.setStatus("dnd");
	},
	MessageCreate: async message => {
		// ignoring messages that aren't from the development server
		if (message.guild.id !== config.guildId) return;

		// don't react to the bot sending messages
		if (message.author == client.user.id) return;

		// automatically embed a post if there is a valid ifunny link in it
		if (isValidiFunnyLink(message.content)) {
			// logging
			console.log(`Embedding content from ${message.content}`);

			// extracting the post in the message
			extractPost(message.content,
				resolve => {
					message.reply(resolve);
				},
				_ => {
					return;
				}
			)
		}
	},
	InteractionCreate: async interaction => {
		if (!interaction.isChatInputCommand()) return;

		// filtering through the commands to find the requested command
		const [command] = client.commands.filter(command => {
			return command.data.name === interaction.commandName;
		});

		// just in case the command that was called is undefined
		if (command === undefined) {
			const msg = `You somehow tried to call an undefined command "${interaction.commandName}" Good job!`;
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
				content: `An error occurred using ${interaction.commandName}`,
				ephemeral: true,
			});
		}
	},
	Put: async (payload) => {
		return await rest.put(
			Routes.applicationGuildCommands(config.clientId, config.guildId),
			{ body: payload }
		);
	}
}

const prod = {
	ClientReady: c => {
		console.log(`Ready! Logged in as ${c.user.tag}`);

		// setting the activity
		client.user.setActivity("Use /about for the bot!");
	},
	MessageCreate: async message => {
		// don't react to the bot sending messages
		if (message.author == client.user.id) return;

		// automatically embed a post if there is a valid ifunny link in it
		if (isValidiFunnyLink(message.content)) {
			// logging
			console.log(`Embedding content from ${message.content}`);

			// extracting the post in the message
			extractPost(message.content,
				resolve => {
					message.reply(resolve);
				},
				_ => {
					return;
				}
			)
		}
	},
	InteractionCreate: async interaction => {
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
	},
	Put: async (payload) => {
		// establishing a rest connection to discord
		const rest = new REST({ version: "10" }).setToken(config.token);

		return await rest.put(
			Routes.applicationCommands(config.clientId),
			{ body: payload }
		);
	}
}

export { client, dev, prod };

