import { AttachmentBuilder, SlashCommandBuilder } from "discord.js";
import { JSDOM } from "jsdom";
import request from "request";
import { getExportFormat, sanitizeUsername } from "../utils/utils.js";
import { pullServerConfigNoInsert } from "../utils/db.js";
import { request_image } from "../utils/format_image.js";

async function icon(interaction) {
    // deferring the reply
    await interaction.deferReply();

    // pulling the server config
    const config = await pullServerConfigNoInsert(interaction.guild.id);

    // getting the user to search for
    /** @type String */
    const raw_username = interaction.options.getString("name");

    // logging
    console.log(`Looking user "${raw_username}"...`);

    // forming the URL of the potential user
    const url = `https://ifunny.co/user/${raw_username}`;

    /** @type String */
    const username = sanitizeUsername(raw_username);

    /// posting to the URL

    // trying to get an HTTP request from that url
    request(url, { json: true }, (err, res, _) => {
        if (err) {
            console.log("An error occurred:", err);
            return interaction.editReply("An error talking to iFunny servers.");
        }
        if (res) {
            if (res.statusCode !== 200) {
                const msg = `User ${username} could not be found.`;
                console.log(msg);
                return interaction.editReply(msg);
            } else {
                // logging
                console.log(`Found user ${username}.`);

                // turning the payload into something parse-able
                const dom = new JSDOM(res.body).window.document;

                // parsing the icon
                var icon;
                const iconEl = dom.querySelector(
                    "span._4nz- > span.F6b- > img.k3q9"
                );
                if (iconEl) {
                    // user has an avatar
                    icon = iconEl.getAttribute("src");
                } else {
                    // no avatar if here
                    console.log(`User ${username} has no icon.`);

                    // breaking early
                    return interaction.editReply(`${username} has the default profile picture.`);
                }

                // choosing export image format
                const __format = getExportFormat(config.exportFormat);

                // creating callbacks
                const resolve = (file) => {
                    const files = new AttachmentBuilder()
                        .setFile(file)
                        .setName(`${username}_pfp.png`);

                    const message = `${username}'s profile picture.`;

                    // editing the response
                    return interaction.editReply({ content: message, files: [files] });
                };

                const error = (message) => {
                    console.log(message);
                    return interaction.editReply(`There was an error formatting the image to ${__format}.`);
                };

                // calling the function
                return request_image(icon, __format, false, resolve, error);
            }
        }
    });
}

const Icon = {
    data: new SlashCommandBuilder()
        .setName("icon")
        .setDescription(
            "Retrieves a user's profile picture. (case insensitive)"
        )
        .addStringOption(option => {
            return option
                .setName("name")
                .setDescription("The user's name.")
                .setRequired(true);
        }),
    execute: icon,
};

export default Icon;
