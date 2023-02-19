import { SlashCommandBuilder, EmbedBuilder } from "discord.js";

const avatarIcon = "https://imageproxy.ifunny.co/crop:square,resize:100x,quality:90/user_photos/57459299098918f644f560dc5e73e0c4a10c9495_0.webp";
const iFunnyIcon = "https://play-lh.googleusercontent.com/Wr4GnjKU360bQEFoVimXfi-OlA6To9DkdrQBQ37CMdx1Kx5gRE07MgTDh1o7lAPV1ws";

const footerQuotes = [
	{ quote: "Go out and be based.", author: "anonymous" },
	{ quote: "A based man in a cringe place makes all the difference.", author: "The G-Man" },
	{ quote: "It's good to be king. Wait, maybe. I think maybe I'm just like a little bizarre little person who walks back and forth. Whatever, you know, but...", author: "Terry Davis" },
	{ quote: "All my characters are me. I'm not a good enough actor to become a character. I hear about actors who become the role and I think 'I wonder what that feels like.' Because for me, they're all me.", author: "Ryan Gosling" },
	{ quote: "I gotta fart", author: "me"},
	{ quote: "Do not compare yourself to others. If you do so, you are insulting yourself.", author: "anonymous" },
	{ quote: "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.", author: "John 3:16" },
	{ quote: "Why should you feel anger at the world? As if the world would notice.", author: "Marcus Aurelius" },
	{ quote: "What? Rappers say it all the time.", author: "Asuka Soryu" },
	{ quote: "Wash your penis.", author: "Jorden Peterson" },
	{ quote: "I am a federal agent.", author: "I'm being serious" },
	{ quote: "Imagine being so universally despised that there has to be laws to prevent people from hating you.",
		author: "anonymous" },
	{ quote: "He's literally me.", author: "Ryan Gosling" }
];

function randomQuote(list) {
	// choosing the quote
	const quote = list[Math.floor(Math.random() * list.length)];

	// joining the fields
	return `"${quote.quote}" - ${quote.author}`;
}		

async function about(interaction) {
	// creating the embed
	const embed = new EmbedBuilder()
		.setColor(0x0099FF)
		.setTitle("Source Code")
		.setAuthor({ name: "bruhulance.if", iconURL: avatarIcon })
		.setURL("https://github.com/JimAppreciator512/ifunny-bot")
		.setDescription("This is a bot which uses webscraping to embed iFunny.co links into discord.")
		.setThumbnail(iFunnyIcon)
		.setFooter({ text: randomQuote(footerQuotes) });
	
	// replying with the embed
	return interaction.reply({ embeds: [embed] });
}

const About = {
	data: new SlashCommandBuilder()
		.setName("about")
		.setDescription("Replies with a description of the bot."),
	execute: about
};

export default About;

