/**
 * @typedef Payload
 * @prop {String} username
 * @prop {String} iconUrl
 * @prop {String} likes
 * @prop {String} comments
 * @prop {String|Object} content
 */

/**
 * @returns {Payload}
 */
const defaultPayload = () => {
    return {
        username: "",
        iconUrl: "",
        likes: 0,
        comments: 0,
    };
};

export { defaultPayload };
