import { EmbedBuilder, SlashCommandBuilder } from "discord.js";
import { JSDOM } from "jsdom";
import request from "request";
import { iFunnyIcon } from "../utils/misc.js";

async function user(interaction) {
	// getting the user to search for
	/** @type String */
	const input = interaction.options.getString("name");

	// does javascript even have buffer overflows?
	if (input.length > 100) {
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
				// turning the payload into something parse-able
				const dom = new JSDOM(res.body).window.document;

				// parsing the icon
				var icon;
				const iconEl = dom.querySelector("span._4nz- > span.F6b- > img.k3q9")
				if (iconEl) {
					// user has an avatar
					icon = iconEl.getAttribute("src");
				} else {
					// no avatar if here
					icon = iFunnyIcon;
				}

				// getting the description
				const description = dom.querySelector("div.Hi31 > div.vjX5").textContent;

				// parsing the sub count
				const subCount = / (.*) subscriber/.exec(
					dom.querySelector("div.Hi31 > div[class='g+J7'] > a.sWk7").textContent)[1]

				// parsing the number of features
				const featureCount = dom.querySelector("div.Hi31 > div._2tcI").textContent.trim();
				
				// forming the footer of the embed
				const footer = `${subCount} subcribers - ${featureCount}`;

				// creating a nice embed
				const embed = new EmbedBuilder()
					.setColor(0x0099ff)
					.setTitle(input)
					.setURL(url)
					.setThumbnail(icon)
					.setDescription(description)
					.setFooter({ text: footer })

				// return the result of interaction.reply
				return interaction.reply({ embeds: [embed] });
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
