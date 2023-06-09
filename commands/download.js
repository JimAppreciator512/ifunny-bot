import { SlashCommandBuilder, ChatInputCommandInteraction } from "discord.js";
import extractPost from "../utils/extractpost.js";

/**
 * this function is a nice wrapper around the `extractPost` function
 * @param {ChatInputCommandInteraction} interaction the slash command
 */
async function download(interaction) {

	// deferring the reply later
	await interaction.deferReply();

	/// shorthands to reply to a message
	// this should only accept a string
	const ereply = message => {
		return interaction.editReply({ content: message, ephemeral: true });
	};

	// can accept either an object payload or a string
	const reply = message => {
		if (typeof message === "object") {
			return interaction.editReply(message)
		}
		return interaction.editReply({ content: message });
	};

	// getting the url to search in
	/** @type String */
	const url = interaction.options.getString("link");

	// extracting the post
	await extractPost(url, reply, ereply);
}

const Download = {
	data: new SlashCommandBuilder()
		.setName("download")
		.setDescription("Downloads a video/image from iFunny.")
		.addStringOption(option => {
			return option
				.setName("link")
				.setDescription("An iFunny.co link e.g., ifunny.co/video/...")
				.setRequired(true);
		}),
	execute: download,
};

export default Download;

