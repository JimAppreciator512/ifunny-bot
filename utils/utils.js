export const ifunnyLinkPattern =
    /(https:\/\/ifunny.co\/(picture|video|gif|meme)\/(.*){1,20}(\?.*){0,20})/;
export const ifunnyLinkDatatype = /(picture|video|gif|meme)/;

export function isValidiFunnyLink(url) {
    // testing if the url is from the expected domain
    return url.match(ifunnyLinkPattern) !== null;
}

export function extractiFunnyLink(content) {
    // extracting the ifunny url from the content
    const match = content.match(ifunnyLinkPattern);
    if (match !== null) {
        return match[0];
    } else {
        return null;
    }
}

export function extractDatatype(url) {
    // getting the datatype of the url
    return url.match(ifunnyLinkDatatype)[1];
}

export const imageExportFormats = [
    "png",
    "heif"
];

