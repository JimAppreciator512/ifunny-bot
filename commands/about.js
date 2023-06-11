import { SlashCommandBuilder, EmbedBuilder } from "discord.js";
import { randomQuote, iFunnyIcon, avatarIcon } from "../utils/misc.js"; 

async function about(interaction) {
	// creating the embed
	const embed = new EmbedBuilder()
		.setColor(0x0099FF)
		.setTitle("Source Code")
		.setAuthor({ name: "bruhulance.if", iconURL: avatarIcon })
		.setURL("https://github.com/JimAppreciator512/ifunny-bot")
		.setDescription("Mainly uses slash commands (/), will auto-parse iFunny.co links in messages.")
		.setThumbnail(iFunnyIcon)
		.setFooter({ text: randomQuote() });
	
	// replying with the embed
	return interaction.reply({ embeds: [embed] });
}

const About = {
	data: new SlashCommandBuilder()
		.setName("about")
		.setDescription("Replies with a description of the bot and a link to the source code."),
	execute: about
};

export default About;

