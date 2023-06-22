import { SlashCommandBuilder, EmbedBuilder } from "discord.js";
import { randomQuote } from "../utils/misc.js";
import Post from "./post.js";
import User from "./user.js";
import About from "./about.js";

const commands = [Post, User, About];

const fields = [
    ...commands.map(cmd => {
        return {
            name: "/" + cmd.data.name,
            value: cmd.data.description,
        };
    }),
    {
        name: "Message",
        value: "If any message sent contains a link to a post on iFunny, it will auto execute the /post function.",
    },
];

const embed = new EmbedBuilder()
    .setColor(0x0099ff)
    .setTitle("Help")
    .setDescription("List of all commands")
    .setFields(...fields)
    .setFooter({ text: randomQuote() });

const Help = {
    data: new SlashCommandBuilder()
        .setName("help")
        .setDescription("Shows all the commands for the bot and what they do."),
    execute: async interaction => {
        await interaction.reply({ embeds: [embed] });
    },
};

export default Help;
