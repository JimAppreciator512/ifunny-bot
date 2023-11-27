import { EmbedBuilder, SlashCommandBuilder } from "discord.js";
import { JSDOM } from "jsdom";
import request from "request";
import { iFunnyIcon } from "../utils/misc.js";
import { sanitizeUsername } from "../utils/utils.js";

async function user(interaction) {
    // deferring the reply
    await interaction.deferReply();

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
                    icon = iFunnyIcon;
                    console.log(`User ${username} has no icon.`);
                }

                // getting the description
                const description = (() => {
                    try {
                        return dom.querySelector("div.Hi31 > div.vjX5")
                            .textContent;
                    } catch (error) {
                        return "No description.";
                    }
                })();

                // parsing the sub count
                const subCount = (() => {
                    try {
                        return / (.*) subscriber/.exec(
                            dom.querySelector(
                                "div.Hi31 > div[class='g+J7'] > a.sWk7"
                            ).textContent
                        )[1];
                    } catch (error) {
                        return "No subscribers.";
                    }
                })();

                // parsing the number of features
                const featureCount = (() => {
                    try {
                        return dom
                            .querySelector("div.Hi31 > div._2tcI")
                            .textContent.trim();
                    } catch (error) {
                        return "No features.";
                    }
                })();

                // forming the footer of the embed
                const footer = `${subCount} subcribers - ${featureCount}`;

                // creating a nice embed
                const embed = new EmbedBuilder()
                    .setColor(0x0099ff)
                    .setTitle(username)
                    .setURL(url)
                    .setThumbnail(icon)
                    .setDescription(description)
                    .setFooter({ text: footer });

                // editing the response
                return interaction.editReply({ embeds: [embed] });
            }
        }
    });
}

const User = {
    data: new SlashCommandBuilder()
        .setName("user")
        .setDescription(
            "Embeds the link to a user's profile. (case insensitive)"
        )
        .addStringOption(option => {
            return option
                .setName("name")
                .setDescription("The user's name.")
                .setRequired(true);
        }),
    execute: user,
};

export default User;
