import { SlashCommandBuilder, AttachmentBuilder } from "discord.js";
import request from "request";
import { JSDOM } from "jsdom";
import Clipper from "image-clipper";
import Canvas from "canvas";
import dataUriToBuffer from "data-uri-to-buffer";

// configuring image cropping
Clipper.configure({
	canvas: Canvas
});

const helpMsg =
	"Usage: /download link: https://ifunny.co/(picture|video|gif)/...";

/**
 * a macro to quickly log to the console/file and discord
 */
function cdlog(message) {	
	console.log(message);
	return interaction.reply({ content: message, ephemeral: true });
}

async function download(interaction) {
	// getting the url to search in
	/** @type String */
	const url = interaction.options.getString("link");

	// logging
	console.log(`Looking in ${url}...`);

	/// url validation

	// testing if the url is from the expected domain
	const correctURL = /^https:\/\/ifunny\.co\/(picture|video|gif)/;
	const datatype = url.match(correctURL)[1];
	if (datatype === undefined || datatype === null) {
		// the link is invalid
		console.log(`${url} is an invalid link.`);
		return interaction.reply({ content: helpMsg, ephemeral: true });
	}

	/// posting to the URL

	// trying to get an HTTP request from that url
	request(url, { json: true }, (err, res, _) => {
		if (err) {
			console.log("An error occurred", err);
			return interaction.reply(
				"Something went wrong when making the HTTP request."
			);
		}
		if (res) {
			// transforming the paylod into a DOM
			const dom = new JSDOM(res.body);

			// making selectors
			const dataset = {
				gif: ['head > link[as="image"]', "href"],
				picture: ["div._3ZEF > img", "src"],
				video: ["div._3ZEF > div > video", "data-src"]
			};

			// getting the selector and attribute
			const [selector, attribute] = dataset[datatype];

			// searching the DOM for a datatype tag
			const el = dom.window.document.querySelector(selector);

			// validation
			if (el === null) {
				return cdlog(msg);
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
				const fname = result.match(fpattern)[1] ?? "picture";
				console.log("setting filename", fname);

				// starting Clipper
				const image = Clipper(result, function() {
					// getting dimensions
					var height = this.getCanvas().height;
					var width = this.getCanvas().width;

					// cropping and uploading
					this.crop(0, 0, width, (height - 20))
						.toDataURL(function(cropped) {
							interaction.reply({
								files: [
									new AttachmentBuilder()
										.setName(fname)
										.setFile(dataUriToBuffer(cropped))
								]});
						});
				});
			} else {
				// logging
				console.log(`Returning with the ${datatype} from ${result}`);

				// replying to the user with the url
				return interaction.reply(result);
			}
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
				.setDescription("An iFunny.co link e.g., ifunny.co/video/...")
				.setRequired(true);
		}),
	execute: download,
};

export default Download;
