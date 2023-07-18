// new file for configuring the bot on a server basis
import { PermissionFlagsBits, SlashCommandBuilder } from "discord.js";
import {
    prisma,
    pullServerConfig,
    pullServerConfigNoInsert,
} from "../utils/db.js";

/**
 * this function shows the configuration, enables or disables auto-embed
 * @param {import("discord.js").Interaction} interaction the discord interaction
 */
async function configAutoEmbed(interaction) {
    const data = interaction.options.getBoolean("value");

    // getting the current value of autoEmbed
    const config = await pullServerConfigNoInsert(interaction.guild.id);

    // user wants to display the current setting
    if (data === null) {
        // responding to caller
        return await interaction.editReply({
            ephemeral: true,
            content: config.globalEmbed
                ? "(default) Auto-embedding is set to true, any message in any channel that contains an iFunny link will be embedded."
                : 'Auto-embedding is set to false, any message in any channel that contains an iFunny link will be ignored. This can be overridden if there are channels set via. "/config channels"',
        });
    }

    // user wants to set the configuration
    if (config.globalEmbed === data) {
        // breaking early here since there is no point changing true to true
        return await interaction.editReply(`Set "auto-embed" to ${data}`);
    }
    const result = await prisma.config.update({
        where: {
            server: interaction.guild.id,
        },
        data: {
            globalEmbed: data,
        },
    });

    // evaluating the response
    if (result && result.globalEmbed === data) {
        return await interaction.editReply(`Set "auto-embed" to ${data}`);
    } else {
        return await interaction.editReply(
            `There was an error updating "auto-embed".`
        );
    }
}

/**
 * this function shows the configuration, sets or updates the set "role"
 * @param {import("discord.js").Interaction} interaction the discord interaction
 */
async function configRole(interaction) {
    const data = interaction.options.getRole("role");

    // getting the current value of autoEmbed
    const config = await pullServerConfigNoInsert(interaction.guild.id);

    // user wants to display the current setting
    if (data === null) {
        // responding to caller
        return await interaction.editReply({
            ephemeral: true,
            content:
                config.role !== ""
                    ? `The saved role is ${
                          interaction.guild.roles.resolve(config.role).name
                      }.`
                    : `There is no saved role for this server.`,
        });
    }

    // mapping the id to the actual name to make more sense
    const roleName = interaction.guild.roles.resolve(data.id).name;

    // user wants to set the configuration
    if (config.role === data) {
        // breaking early here since there is no point changing true to true
        return await interaction.editReply(`Set "role" to ${roleName}`);
    }
    const result = await prisma.config.update({
        where: {
            server: interaction.guild.id,
        },
        data: {
            role: data.id,
        },
    });

    // evaluating the response
    if (result && result.role === data.id) {
        return await interaction.editReply(`Set "role" to ${roleName}`);
    } else {
        return await interaction.editReply(
            `There was an error updating "role" to ${roleName}.`
        );
    }
}

async function configChannels(interaction) {}

/**
 * the handler function for the "Config" command
 * @param {import("discord.js").Interaction} interaction the discord interaction
 */
async function config(interaction) {
    // deferring the reply
    await interaction.deferReply();

    // check if the server is saved in the database
    // if saved, continue
    // else,
    //  add the server to the database
    const config = await pullServerConfig(interaction.guild.id);

    // checking if the user has Administrator or ManageGuild
    if (
        !interaction.memberPermissions.has(
            PermissionFlagsBits.ManageGuild | PermissionFlagsBits.Administrator
        )
    ) {
        // user doesn't have ManageGuild nor are they Administrator
        // checking if there is a saved role in this server, the user could still execute this command
        if (config.role !== "") {
            // logging
            console.log(
                `There is a saved role for server ${config.server}, checking if user ${interaction.user.username} has it.`
            );

            // if caller has saved role, continue
            // else, abort
            if (!interaction.member.roles.cache.has(config.role)) {
                // this looks fucking stupid
                console.log(
                    `User ${interaction.user.username} doesn't have the set role, they cannot execute Config.`
                );
                return interaction.editReply({
                    ephemeral: true,
                    content: `You do not have the role ${
                        interaction.guild.roles.resolve(config.role).name
                    }.`,
                });
            }
        } else {
            // logging
            console.log(
                `There is no saved role for server ${config.server}. User ${interaction.user.username} cannot execute Config.`
            );
            return interaction.editReply({
                ephemeral: true,
                content:
                    "You do not have the required permissions to execute this command.",
            });
        }
    }

    /// delegating to smaller functions

    // I don't think there will be more than one entry in `options.data`
    const option = interaction.options.data[0].name;

    // logging
    console.log(
        `User ${interaction.user.username} has valid permissions, they can execute ${option}.`
    );

    switch (option) {
        case "autoembed":
            return await configAutoEmbed(interaction);
        case "channels":
            return await configChannels(interaction);
        case "role":
            return await configRole(interaction);
        default:
            return interaction.editReply(
                `Cannot configure unknown option ${option}.`
            );
    }
}

const Config = {
    data: new SlashCommandBuilder()
        .setName("config")
        .setDescription(
            "Exposes configuration tools to control how the bot behaves on this server."
        )
        .addSubcommand(subcommand => {
            return subcommand
                .setName("autoembed")
                .setDescription(
                    "Controls whether the bot auto-embeds posts found in messages in any channel."
                )
                .addBooleanOption(option => {
                    return option
                        .setName("value")
                        .setDescription("True to enable, false to disable.");
                });
        })
        .addSubcommand(subcommand => {
            return subcommand
                .setName("channels")
                .setDescription(
                    "Whitelisted channels the bot will autoembed in."
                )
                .addChannelOption(option => {
                    return option
                        .setName("channel")
                        .setDescription("The channel to listen in.");
                });
        })
        .addSubcommand(subcommand => {
            return subcommand
                .setName("role")
                .setDescription(
                    'The role that can configure the bot. (default "manage server" or "administrator")'
                )
                .addRoleOption(option => {
                    return option
                        .setName("role")
                        .setDescription(
                            "The role that can configure the bot ."
                        );
                });
        }),
    execute: config,
};

export default Config;
