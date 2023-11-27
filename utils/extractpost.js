import request from "request";
import {
    extractDatatype,
    extractiFunnyLink,
    getExportFormat,
    imageExportFormats,
    scrapePostInformation,
} from "../utils/utils.js";
import { AttachmentBuilder } from "discord.js";
import { JSDOM } from "jsdom";
import { EmbedBuilder } from "@discordjs/builders";
import { chooseRandomPost } from "../utils/misc.js";
import { request_image } from "./format_image.js";

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
                var __el, sel, attr;
                var __d = d;

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
                match[2] === "jpg" ? format : match[2]
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

                // returning the cropped image from the url
                return request_image(contentUrl, format, true, (file) => {
                    resolve({
                        files: [
                            new AttachmentBuilder()
                                .setName(fname)
                                .setFile(file),
                        ],
                        embeds: [embed],
                    });
                },
                    () => {
                    console.log("There was an error cropping the image.");
                    return err("There was an error cropping the image.");
                });
            }
        });
    } catch (e) {
        console.log("ERR: AAAAAAAAAAAAAAAAAAAAAAAA"); // just something to grep for
        console.log(e);
        return err("Something unknown happened, contact the dev.");
    }
}

export default extractPost;
