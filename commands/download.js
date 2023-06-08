import { SlashCommandBuilder, ChatInputCommandInteraction } from "discord.js";
import extractPost from "./extractpost.js";

/**
 * @param {ChatInputCommandInteraction} interaction the slash command
 */
async function download(interaction) {

	// deferring the reply later
	await interaction.deferReply();

	/// shorthands to reply to a message
	const ereply = message => {
		return interaction.editReply({ content: message, ephemeral: true });
	};

	const reply = message => {
		if (typeof message === "object") {
			return interaction.editReply(message)
		}
		return interaction.editReply({ content: message });
	};

	// getting the url to search in
	/** @type String */
	const url = interaction.options.getString("link");

	// looking for buffer overflow
	if (url.length > 100) {
		console.log("Rejecting url:\n", url);
		return ereply("Invalid link entered.");
	}

	/// extracting the post
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

