import { SlashCommandBuilder } from "discord.js";
import request from "request";
import { JSDOM } from "jsdom";

async function download(interaction) {
	// getting the url to search in
	/** @type String */
	const url = interaction.options.getString("link");

	// logging
	console.log(`Looking in ${url}...`);

	/// url validation

	// testing if the url is from the expected domain
	const correctURL = /https:\/\/ifunny\.co/;
	if (!url.match(correctURL)) {
		// the link is invalid
		const msg = `${url} is an invalid link.`;
		console.log(msg);
		return interaction.reply(msg);
	}
	
	// for optimization, look at the URL to see whether it's an image or video
	const datatype = /\/(picture|video)/;
	if (!url.match(datatype)) {
		// the link is invalid
		const msg = `${url} is an invalid iFunny.co link.`;
		console.log(msg);
		return interaction.reply(msg);
	}
	
	// it passed the check, establishing what kind of data we're dealing with
	const isImage = url.match(datatype)[1] === "picture";

	// logging
	console.log(`Found ${isImage ? "an image" : "a video"} at ${url}`);

	// trying to get an HTTP request from that url
	request(url, { json: true }, (err, res, _) => {
		if (err) {
			console.log("An error occurred", err);
			return interaction.reply("Something went wrong when making the HTTP request.")
		}
		if (res) {
			// transforming the paylod into a DOM
			const dom = new JSDOM(res.body);

			// forming the selector to look at
			const sel = isImage ? "div._3ZEF > img" : "div._3ZEF > div > video";
			
			// searching the DOM for a video/image tag
			const result = dom.window.document.querySelector(sel)
				// need to grab a conditional attribute based on the content type
				.getAttribute(isImage ? "src" : "data-src");

			// logging
			console.log(`Returning with the ${isImage ? "image" : "video"} from ${result}`);
				
			// replying to the user with the url
			return interaction.reply(result);
		}
	});
}

const Download = {
	data: new SlashCommandBuilder()
		.setName("download")
		.setDescription("Downloads a video/image from iFunny.")
		.addStringOption(option => {
			return option
				.setName("link")
				.setDescription("The link to look in")
				.setRequired(true);
		}),
	execute: download
};

export default Download;

