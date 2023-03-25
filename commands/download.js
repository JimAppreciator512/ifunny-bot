import { JSDOM } from "jsdom";
import { SlashCommandBuilder, AttachmentBuilder } from "discord.js";
import Canvas from "canvas";
import Clipper from "image-clipper";
import request from "request";
import dataUriToBuffer from "data-uri-to-buffer";

// configuring image cropping
Clipper.configure({
	canvas: Canvas,
});

const helpMsg =
	"Usage: /download link: https://ifunny.co/(picture|video|gif)/...";

async function download(interaction) {
	// quick shorthand to reply to a message
	const reply = message => {
		return interaction.reply({ content: message, ephemeral: true });
	};

	// getting the url to search in
	/** @type String */
	var url = interaction.options.getString("link");

	// looking for buffer overflow
	if (url.length > 100) {
		console.log("Rejecting url:\n", url);
		return interaction.reply("Url is an invalid link.");
	}

	// logging
	console.log(`Looking in ${url}...`);

	/// url validation

	// testing if the url is from the expected domain
	const correctURL = /^https:\/\/ifunny\.co\/(picture|video|gif|meme)/;
	const match = url.match(correctURL);
	if (match === null) {
		// the link is invalid
		const msg = `${url} is an invalid link.`;
		console.log(msg);
		return reply(msg);
	} else if (match[1] === "meme") {
		// datatype unset
		console.log(`Content at ${url} has been unset, trying to fix.`);
		url = url.replace("meme", "picture");
	}

	// getting the datatype from the url
	var datatype = match[1];

	/// posting to the URL

	// trying to get an HTTP request from that url
	try {
		request(url, { json: true }, (err, res, _) => {
			if (err) {
				console.log("An error occurred", err);
				return reply(
					"Something went wrong when making the HTTP request."
				);
			}
			if (res) {
				// looking at the status code
				if (res.statusCode !== 200) {
					const msg = `Meme at ${url} has been removed.`;
					console.log(msg);
					return reply(msg);
				}

				// transforming the paylod into a DOM
				const dom = new JSDOM(res.body);

				// making selectors
				const dataset = {
					picture: ["div._3ZEF > img", "src"],
					video: ["div._3ZEF > div > video", "data-src"],
					gif: ['head > link[as="image"]', "href"],
				};

				// HTML related elements
				var el, selector, attribute;

				// if content is meme, guess the selector
				if (datatype === "meme") {
					for (const key of Object.keys(dataset)) {
						// getting the selector and attribute
						[selector, attribute] = dataset[key];

						// trying to find the element
						el = dom.window.document.querySelector(selector);

						// if null, loop, else return false from func
						if (el !== null) {
							// updating the datatype
							datatype = key;
							break;
						}
						console.log(`Couldn't find ${key} at ${url}.`);
					}
					// content is not meme, therefore we can extract the selector without guessing
				} else {
					// getting the selector and attribute
					[selector, attribute] = dataset[datatype];

					// searching the DOM for a datatype tag
					el = dom.window.document.querySelector(selector);
				}

				// testing if the element is null after looking at all
				// combinations.
				if (el === null) {
					const msg = `Couldn't find ${datatype} at ${url}.`;
					console.log(msg);
					return reply(msg);
				}

				// logging
				console.log(`Found a ${datatype} at ${url}`);

				// need to grab a conditional attribute based on the content type
				const result = el.getAttribute(attribute);

				// auto-cropping the image if it is a picture
				if (datatype === "picture") {
					console.log(`Cropping picture found at ${url}...`);

					// getting the filename
					const fpattern = /co\/\w+\/(.*\.\w{3})$/;
					const fname =
						result.match(fpattern)[1] ?? `ifunny_${datatype}`;
					console.log("Setting filename", fname);

					// starting Clipper
					const image = Clipper(result, function () {
						// getting dimensions
						var height = this.getCanvas().height;
						var width = this.getCanvas().width;

						// cropping and uploading
						this.crop(0, 0, width, height - 20).toDataURL(function (
							cropped
						) {
							// uploading the cropped image
							interaction.reply({
								files: [
									new AttachmentBuilder()
										.setName(fname)
										.setFile(dataUriToBuffer(cropped)),
								],
							});
						});
					});
				} else {
					// logging
					console.log(
						`Returning with the ${datatype} from ${result}`
					);

					// replying to the user with the url
					return interaction.reply(result);
				}
			}
		});
	} catch (e) {
		console.log("ERR: AAAAAAAAAAAAAAAAAAAAAAAA"); // just something to grep for
		console.log(e);
		return interaction.reply(
			"Something unknown happened, contact the dev."
		);
	}
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
