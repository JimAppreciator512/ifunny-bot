import request from "request";
import sharp from "sharp";
import { Buffer } from "node:buffer";
import { extractDatatype, extractiFunnyLink } from "./utils.js";
import { AttachmentBuilder } from "discord.js";
import { JSDOM } from "jsdom";

/**
 * this function does the heavy lifting by making an HTTP request to the iFunny link
 * you need the `resolve` and `err` methods because trying to return out of the `request` block
 * just doesn't work, also different use cases
 * @param {String} content the content to be parsed
 * @param {function(String)} resolve a way to send a message to discord
 * @param {function(String)} err a way to send an error message to the user
 */
async function extractPost(content, resolve, err) {	
	// extracting the url from the string
	const url = extractiFunnyLink(content);
	if (url === null) {
		return err("Invalid url.");
	}
	
	// looking for buffer overflow
	if (url.length > 100) {
		console.log("Rejecting url:\n", url);
		return ereply("Invalid link entered.");
	}

	// logging
	console.log(`Looking in ${url}...`);

	// parsing the datatype from the url
	var datatype = extractDatatype(url);

	// trying to get an HTTP request from that url
	try {
		request(url, (err, res, _) => {
			if (err) {
				console.log("An error occurred", err);
				return err("Something went wrong when making the HTTP request.");
			}
			if (res) {
				// looking at the status code
				if (res.statusCode !== 200 || res.statusCode >= 400) {
					const msg = `Meme at ${url} has been removed.`;
					console.log(msg);
					return err(msg);
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
				} else {
					// content is not meme, therefore we can extract the selector without guessing

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
					return err(msg);
				}

				// logging
				console.log(`Found a ${datatype} at ${url}`);

				// need to grab a conditional attribute based on the content type
				const result = el.getAttribute(attribute).replaceAll("jpg", "webp");

				// auto-cropping the image if it is a picture
				if (datatype === "picture") {
					console.log(`Cropping picture found at ${url}...`);

					// getting the filename
					const fpattern = /co\/\w+\/(.*\.\w{4})$/;
					const fname =
						(result.match(fpattern)[1] ?? `ifunny_${datatype}.webp`).replaceAll("webp", "png");
					console.log("Setting filename", fname);

					// requesting the image from the source
					request({ uri: result, encoding: null }, (err, res, body) => {
						// there was an error in transit
						if (err) {
							console.log("Error during HTTP request for image", err);
							return err("There was an error getting the source of the image.");
						}

						// erroring if the code isn't 200 or a client/server error
						if (res.statusCode !== 200 && res.statusCode >= 400) {
							// theoretically, the code should never get here
							console.log("The status code isn't 200", err);
							return err("There was an error getting the source of the image.");
						}

						/// using Sharp because Clipper is shit
						const image = sharp(Buffer.from(body));
						image.metadata()
							.then(meta => {
								return image
									.resize({
										width: meta.width,
										height: meta.height - 20,
										position: "top"
									})
									.png()
									.toBuffer({ resolveWithObject: true });
							})
							.then(({ data }) => {
								return resolve({
									files: [
										new AttachmentBuilder()
											.setName(fname)
											.setFile(data)
									]
								});
							})
							.catch(err => {
								console.log("Error during image cropping.", err);
								return err("There was an error while cropping the image.");
							});

					});
				} else {
					// logging
					console.log(
						`Returning with the ${datatype} from ${result}`
					);

					// replying to the user with the url
					resolve(result);
				}
			}
		});
	} catch (e) {
		console.log("ERR: AAAAAAAAAAAAAAAAAAAAAAAA"); // just something to grep for
		console.log(e);
		return err("Something unknown happened, contact the dev.");
	}
}

export default extractPost;

