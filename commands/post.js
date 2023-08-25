import { SlashCommandBuilder, ChatInputCommandInteraction } from "discord.js";
import extractPost from "../utils/extractpost.js";
import { pullServerConfigNoInsert } from "../utils/db.js";

/**
 * this function is a nice wrapper around the `extractPost` function
 * @param {ChatInputCommandInteraction} interaction the slash command
 */
async function post(interaction) {
    // deferring the reply later
    await interaction.deferReply();

    /// shorthands to reply to a message
    // this should only accept a string
    const ereply = message => {
        return interaction.editReply({ content: message, ephemeral: true });
    };

    // can accept either an object payload or a string
    const reply = message => {
        if (typeof message === "object") {
            return interaction.editReply(message);
        }
        return interaction.editReply({ content: message });
    };

    // getting the url to search in
    /** @type String */
    const url = interaction.options.getString("link");

    // pulling the server config
    const config = await pullServerConfigNoInsert(interaction.guild.id);

    // extracting the post
    await extractPost(url, reply, ereply, config ? config.exportFormat : "png");
}

const Post = {
    data: new SlashCommandBuilder()
        .setName("post")
        .setDescription("Posts a video/image from iFunny.")
        .addStringOption(option => {
            return option
                .setName("link")
                .setDescription("An iFunny.co link e.g., ifunny.co/video/...")
                .setRequired(true);
        }),
    execute: post,
};

export default Post;
