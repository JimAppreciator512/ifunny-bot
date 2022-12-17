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
	const correctURL = /https:\/\/ifunny\.co\/(picture|video|gif)/;
	let datatype;
	if (!url.match(correctURL)) {
		// the link is invalid
		const msg = `${url} is an invalid link.`;
		console.log(msg);
		return interaction.reply(msg);
	} else {
		datatype = url.match(correctURL)[1];
	}
	
	console.log(`datatype ${datatype}`);

	// evaluating
	if (datatype === null) {
		// the link is invalid
		const msg = `${url} is an invalid iFunny.co link.`;
		console.log(msg);
		return interaction.reply(msg);
	}

	// trying to get an HTTP request from that url
	request(url, { json: true }, (err, res, _) => {
		if (err) {
			console.log("An error occurred", err);
			return interaction.reply("Something went wrong when making the HTTP request.")
		}
		if (res) {
			// transforming the paylod into a DOM
			const dom = new JSDOM(res.body);

			// making selectors
			const selEnum = {
				"gif": "head > link[as=\"image\"]",
				"picture": "div._3ZEF > img",
				"video": "div._3ZEF > div > video"
			}
			const attribEnum = {
				"gif": "href",
				"picture": "src",
				"video": "data-src"
			}

			// getting the selector and attribute
			const sel = selEnum[datatype];
			const attrib = attribEnum[datatype]
			
			// searching the DOM for a datatype tag
			const el = dom.window.document.querySelector(sel);

			// validation
			if (el === null) {
				const msg = `Couldn't find ${datatype} at ${url}`;
				console.log(msg);
				return interaction.reply(msg);
			}

			// logging
			console.log(`Found a ${datatype} at ${url}`);

			// need to grab a conditional attribute based on the content type
			const result = el.getAttribute(attrib);

			// logging
			console.log(`Returning with the ${datatype} from ${result}`);
				
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

