
import { SlashCommandBuilder, AttachmentBuilder } from "discord.js";
import request from "request";

async function user(interaction) {
	// getting the user to search for
	/** @type String */
	const input = interaction.options.getString("name");

	if (input.len > 30) {
		return interaction.reply("That username is too long for me to understand.")
	}

	// logging
	console.log(`Looking user "${input}"...`);

	// forming the URL of the potential user
	const url = `https://ifunny.co/user/${input}`;

	/// posting to the URL

	// trying to get an HTTP request from that url
	request(url, { json: true }, (err, res, _) => {
		if (err) {
			console.log("An error occurred:", err);
			return interaction.reply("An error talking to iFunny servers.");
		}
		if (res) {
			if (res.statusCode === 200) {
				console.log(`Found user ${input}`);
				return interaction.reply(url);
			} else {
				const msg = `User ${input} could not be found.`;
				console.log(msg);
				return interaction.reply(msg);
			}
		}
	});
}

const User = {
	data: new SlashCommandBuilder()
		.setName("user")
		.setDescription("Embeds the link to a user's profile")
		.addStringOption(option => {
			return option
				.setName("name")
				.setDescription("The user's name.")
				.setRequired(true);
		}),
	execute: user,
};

export default User;
