import request from "request";
import sharp from "sharp";
import { Buffer } from "node:buffer";
import { extractDatatype, extractiFunnyLink } from "../utils/utils.js";
import { AttachmentBuilder } from "discord.js";
import { JSDOM } from "jsdom";
import { defaultPayload } from "./payload.js";
import { EmbedBuilder } from "@discordjs/builders";

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

    // logging
    console.log(`Looking in ${url}...`);

    // parsing the datatype from the url
    var datatype = extractDatatype(url);

    // trying to get an HTTP request from that url
    try {
        request(url, (err, res, _) => {
            if (err) {
                console.log("An error occurred", err);
                return err(
                    "Something went wrong when making the HTTP request."
                );
            }
            if (res) {
                // looking at the status code
                if (res.statusCode !== 200 || res.statusCode >= 400) {
                    const msg = `Meme at ${url} has been removed.`;
                    console.log(msg);
                    return err(msg);
                }

                // transforming the paylod into a DOM
                const dom = new JSDOM(res.body).window.document;

                // making selectors
                const dataset = {
                    picture: ["div._3ZEF > img", "src"],
                    video: ["div._3ZEF > div > video", "data-src"],
                    gif: ['head > link[as="image"]', "href"],
                };

                /// getting post statistics
                const payload = defaultPayload();

                payload.username = dom
                    .querySelector("div._9JPE > a.WiQc > span.IfB6")
                    .textContent.replace(" ", "");
                payload.iconUrl = dom
                    .querySelector("div._9JPE > a.WiQc > img.dLxH")
                    .getAttribute("data-src");
                payload.likes = dom.querySelectorAll(
                    "div._9JPE > button.Cgfc > span.Y2eM > span"
                )[0].textContent;
                payload.comments = dom.querySelectorAll(
                    "div._9JPE > button.Cgfc > span.Y2eM > span"
                )[1].textContent;

                console.log(payload);
                const embed = new EmbedBuilder()
                    .setDescription(
                        `${payload.likes} likes.\t${payload.comments} comments.`
                    )
                    .setTitle(`Post by ${payload.username}`)
                    .setURL(url)
                    .setThumbnail(payload.iconUrl);

                // HTML related elements
                var el, selector, attribute;

                // if content is meme, guess the selector
                if (datatype !== "meme") {
                    // getting the selector and attribute
                    [selector, attribute] = dataset[datatype];

                    // searching the DOM for a datatype tag
                    el = dom.querySelector(selector);
                } else {
                    // we need to guess the selector that has the content url
                    for (const key of Object.keys(dataset)) {
                        // getting the selector and attribute
                        [selector, attribute] = dataset[key];

                        // trying to find the element
                        el = dom.querySelector(selector);

                        // if null, loop, else return false from func
                        if (el !== null) {
                            // updating the datatype
                            datatype = key;
                            break;
                        }
                        console.log(`Couldn't find ${key} at ${url}.`);
                    }
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

                // geting the url where the content is stored
                const contentUrl = el.getAttribute(attribute);

                // getting the filename
                const fpattern = /co\/\w+\/(.*\..{3,4})$/;
                const fname =
                    contentUrl.match(fpattern)[1] ?? `ifunny_${datatype}`;

                // logging
                console.log(
                    `Naming the ${datatype} at ${contentUrl} as ${fname}`
                );

                // auto-cropping the image if it is a picture
                if (datatype !== "picture") {
                    // logging
                    console.log(
                        `Returning with the ${datatype} from ${contentUrl}`
                    );

                    // replying to the user with the url
                    resolve({
                        files: [
                            new AttachmentBuilder()
                                .setName(fname)
                                .setFile(contentUrl),
                        ],
                        embeds: [embed],
                    });
                } else {
                    console.log(`Cropping picture found at ${url}...`);

                    // requesting the image from the source
                    request(
                        { uri: contentUrl, encoding: null },
                        (err, res, body) => {
                            // there was an error in transit
                            if (err) {
                                console.log(
                                    "Error during HTTP request for image",
                                    err
                                );
                                return err(
                                    "There was an error while getting the image from the source."
                                );
                            }

                            // erroring if the code isn't 200 or a client/server error
                            if (
                                res.statusCode !== 200 ||
                                res.statusCode >= 400
                            ) {
                                console.log("The status code isn't 200", err);
                                return err(
                                    "There was an error getting the source of the image."
                                );
                            }

                            /// using Sharp because Clipper is shit
                            const image = sharp(Buffer.from(body));
                            image
                                .metadata()
                                .then(meta => {
                                    return image
                                        .resize({
                                            width: meta.width,
                                            height: meta.height - 20,
                                            position: "top",
                                        })
                                        .png() // because png is the best format
                                        .toBuffer({ resolveWithObject: true });
                                })
                                .then(({ data }) => {
                                    return resolve({
                                        files: [
                                            new AttachmentBuilder()
                                                .setName(fname)
                                                .setFile(data),
                                        ],
                                        embeds: [embed],
                                    });
                                })
                                .catch(err => {
                                    console.log(
                                        "Error during image cropping.",
                                        err
                                    );
                                    return err(
                                        "There was an error while cropping the image."
                                    );
                                });
                        }
                    );
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
