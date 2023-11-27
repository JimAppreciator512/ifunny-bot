import request from "request";
import sharp from "sharp";
import { Buffer } from "node:buffer";

export function request_image(image_url, format, crop, resolve, err) {
    // requesting the image from the source
    request(
        { uri: image_url, encoding: null },
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
                    `Couldn't contact the CDN (${image_url}) for the image.`
                );
                return err(
                    "There was an error getting the source of the image."
                );
            }

            // erroring if the code isn't 200 or a client/server error
            if (res2.statusCode === 404) {
                console.error(
                    `The contacting ${image_url} yielded status code ${res2.statusCode}`
                );
                return err(
                    "There was an error getting the source of the image."
                );
            }

            // logging
            console.log(`Found image at ${image_url}, cropping and exporting as ${format}.`);

            // formatting the image
            return format_image(body, format, crop, resolve, err);
        }
    );
}

export function format_image(bytes, format, crop, resolve, error) {
    /// using Sharp because Clipper is shit
    const image = sharp(Buffer.from(bytes));
    image
        .metadata()
        .then(meta => {
            // logging
            console.log("Cropping the image provided.");

            // cropping if enabled
            if (crop) {
                // resizing the image
                image.resize({
                    width: meta.width,
                    height: meta.height - 20, // cropping out the watermark
                    position: "top",
                });
            }

            // logging
            console.log(
                `Exporting image to ${format} format.`
            );

            // formatting the image
            switch (format) {
                case "png":
                    image.png({
                        quality: 85,
                        palette: true,
                    });
                    break;
                case "heif":
                    image.heif({
                        quality: 85,
                        lossless: true,
                    });
                    break;
                default:
                    // defaulting to png
                    image.png({
                        quality: 85,
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
            return resolve(data);
        })
        .catch(__err3 => {
            console.log(
                "Error during image cropping.",
                __err3
            );
            return error(
                "There was an error while cropping the image."
            );
        });
}

