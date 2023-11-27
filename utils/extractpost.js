import request from "request";
import sharp from "sharp";
import { Buffer } from "node:buffer";
import {
    extractDatatype,
    extractiFunnyLink,
    imageExportFormats,
    scrapePostInformation,
} from "../utils/utils.js";
import { AttachmentBuilder } from "discord.js";
import { JSDOM } from "jsdom";
import { EmbedBuilder } from "@discordjs/builders";
import { chooseRandomPost } from "../utils/misc.js";

/**
 * this function does the heavy lifting by making an HTTP request to the iFunny link
 * you need the `resolve` and `err` methods because trying to return out of the `request` block
 * just doesn't work, also different use cases
 * @param {String} content the content to be parsed
 * @param {function(String)} resolve a way to send a message to discord
 * @param {function(String)} err a way to send an error message to the user
 * @param {String} format the target format of the image
 */
async function extractPost(content, resolve, err, format) {
    // extracting the url from the string
    const url = extractiFunnyLink(content);
    if (url === null) {
        // give the user some helpful feedback
        const __url = chooseRandomPost();

        return err(`Invalid url. Sample url: ${__url}`);
    }

    // choosing export image format
    const __format = (f => {
        if (imageExportFormats.includes(f)) {
            return f;
        }
        console.error(`There was an invalid image format specified, ${f}`);
        return "png";
    })(format);

    // logging
    console.log(`Looking in ${url}...`);

    // parsing the datatype from the url
    var datatype = extractDatatype(url);

    // trying to get an HTTP request from that url
    try {
        request(url, (__err, res, _) => {
            if (__err) {
                console.log("An error occurred", __err);
                return err(
                    "Something went wrong when making the HTTP request."
                );
            }

            // if no response
            if (!res || res.statusCode > 404) {
                const msg = "There was an error contacting iFunny servers.";
                console.error(msg);
                return err(msg);
            }

            // if response wasn't 200, the meme was removed
            if (res.statusCode === 404) {
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
            const payload = scrapePostInformation(dom);

            // creating an embed for information about the post
            const embed = new EmbedBuilder()
                .setDescription(
                    `${payload.likes} likes.\t${payload.comments} comments.`
                )
                .setTitle(`Post by ${payload.username}`)
                .setURL(url)
                .setThumbnail(payload.iconUrl);

            // if content is meme, guess the selector
            const [__datatype, contentUrl] = (d => {
                // storing the element we want to scrape the source of the video/image/gif from
                var __el, sel, attr, __d;

                /// if not meme, then directly assign and not guess
                if (d !== "meme") {
                    // getting the selector and attribute
                    [sel, attr] = dataset[d];

                    // searching the DOM for a d tag
                    __el = dom.querySelector(sel);
                } else {
                    // we need to guess the selector that has the content url
                    for (const key of Object.keys(dataset)) {
                        // getting the selector and attribute
                        [sel, attr] = dataset[key];

                        // trying to find the element
                        __el = dom.querySelector(sel);

                        // if null, loop, else return false from func
                        if (__el !== null) {
                            // updating the d
                            __d = key;
                            break;
                        }

                        // logging
                        console.log(`Couldn't find ${key} at ${url}.`);
                    }
                }

                // getting the content url of the video/image/gif
                const __cu = (__el !== null ? __el.getAttribute(attr) : __el);

                return [__d, __cu];
            })(datatype);

            // updating the datatype
            datatype = __datatype;

            // this branches if the program couldn't find the element to scrape the content from
            if (!contentUrl) {
                const msg = `Couldn't find ${datatype} at ${url}.`;
                console.error(msg);
                return err(msg);
            }

            // logging
            console.log(`Found a ${datatype} at ${url}`);

            // getting the filename
            const fpattern = /co\/\w+\/([0-9a-f]*)(?:_\d)?\.(\w{3,4})$/;
            const match = contentUrl.match(fpattern);
            // console.log(match);
            const fname = `${match[1]}.${
                match[2] === "jpg" ? __format : match[2]
            }`;

            // logging
            console.log(`Naming the ${datatype} at ${contentUrl} as ${fname}`);

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
                    (__err2, res2, body) => {
                        // there was an error in transit
                        if (__err2) {
                            console.log(
                                "Error during HTTP request for image",
                                __err2
                            );
                            return err(
                                "There was an error while getting the image from the source."
                            );
                        }

                        // if no response
                        if (!res2 || res2.statusCode > 404) {
                            console.error(
                                `Couldn't contact the CDN (${contentUrl}) for the ${datatype}.`
                            );
                            return err(
                                "There was an error getting the source of the image."
                            );
                        }

                        // erroring if the code isn't 200 or a client/server error
                        if (res2.statusCode === 404) {
                            console.error(
                                `The contacting ${contentUrl} yielded status code ${res2.statusCode}`
                            );
                            return err(
                                "There was an error getting the source of the image."
                            );
                        }

                        /// using Sharp because Clipper is shit
                        const image = sharp(Buffer.from(body));
                        image
                            .metadata()
                            .then(meta => {
                                // resizing the image
                                image.resize({
                                    width: meta.width,
                                    height: meta.height - 20,
                                    position: "top",
                                });

                                // logging
                                console.log(
                                    `Exporting image to ${__format} format.`
                                );

                                // formatting the image
                                switch (__format) {
                                    case "png":
                                        image.png({
                                            quality: 75,
                                            palette: true,
                                        });
                                        break;
                                    case "heif":
                                        image.heif({
                                            quality: 75,
                                            lossless: true,
                                        });
                                        break;
                                    default:
                                        // defaulting to png
                                        image.png({
                                            quality: 75,
                                            palette: true,
                                        });
                                        break;
                                }

                                // returning the image object
                                return image.toBuffer({
                                    resolveWithObject: true,
                                });
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
                            .catch(__err3 => {
                                console.log(
                                    "Error during image cropping.",
                                    __err3
                                );
                                return err(
                                    "There was an error while cropping the image."
                                );
                            });
                    }
                );
            }
        });
    } catch (e) {
        console.log("ERR: AAAAAAAAAAAAAAAAAAAAAAAA"); // just something to grep for
        console.log(e);
        return err("Something unknown happened, contact the dev.");
    }
}

export default extractPost;
