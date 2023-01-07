import { SlashCommandBuilder } from "discord.js";

const Ping = {
	data: new SlashCommandBuilder()
		.setName("ping")
		.setDescription("Replies with pong."),
	execute: async interaction => {
		await interaction.reply("Pong!");
	},
};

export default Ping;
