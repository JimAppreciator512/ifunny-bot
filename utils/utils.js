import { PermissionsBitField } from "discord.js";

export const ifunnyLinkPattern =
    /(https:\/\/ifunny.co\/(picture|video|gif|meme)\/(.*){1,20}(\?.*){0,20})/;
export const ifunnyLinkDatatype = /(picture|video|gif|meme)/;

export function sanitizeUsername(username) {
    // escaping all special characters
    var e_username = username;
    ["\\", "*", "_", "|", "~", ">", "`"].forEach(char => {
        e_username = e_username.replaceAll(char, "\\" + char);
    });

    return e_username;
}

// a function to scrape information about a post
export function scrapePostInformation(html) {
    const payload = {};

    // this will only fail if iFunny every changes their HTML layout
    payload.username = html
        .querySelector("div._9JPE > a.WiQc > span.IfB6")
        .textContent.replace(" ", "");
    payload.iconUrl = html
        .querySelector("div._9JPE > a.WiQc > img.dLxH")
        .getAttribute("data-src");
    payload.likes = html.querySelectorAll(
        "div._9JPE > button.Cgfc > span.Y2eM > span"
    )[0].textContent;
    payload.comments = html.querySelectorAll(
        "div._9JPE > button.Cgfc > span.Y2eM > span"
    )[1].textContent;

    // sanitizing the username's special characters
    payload.username = sanitizeUsername(payload.username);

    return payload;
}

export function isValidiFunnyLink(url) {
    // testing if the url is from the expected domain
    return url.match(ifunnyLinkPattern) !== null;
}

export function extractiFunnyLink(url) {
    // extracting the ifunny url from the content
    const link = url.match(ifunnyLinkPattern);
    if (link !== null) {
        return link[0];
    } else {
        return null;
    }
}

export function extractDatatype(url) {
    // getting the datatype of the url
    return url.match(ifunnyLinkDatatype)[1];
}

export const imageExportFormats = ["png", "heif"];

export const requiredPermissions = [
    PermissionsBitField.Flags.EmbedLinks,
    PermissionsBitField.Flags.SendMessages,
    PermissionsBitField.Flags.AttachFiles,
];

export function getExportFormat(format) {
    return (f => {
        if (imageExportFormats.includes(f)) {
            return f;
        }
        console.error(`There was an invalid image format specified, ${f}`);
        return "png";
    })(format);
}
