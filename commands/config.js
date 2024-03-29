// new file for configuring the bot on a server basis
import { PermissionFlagsBits, SlashCommandBuilder } from "discord.js";
import {
    executeQuery,
    prisma,
    pullServerConfig,
    pullServerConfigNoInsert,
    sha1sum,
} from "../utils/db.js";
import { imageExportFormats } from "../utils/utils.js";

/**
 * this function shows the configuration, enables or disables auto-embed
 * @param {import("discord.js").Interaction} interaction the discord interaction
 */
async function configAutoEmbed(interaction) {
    const data = interaction.options.getBoolean("value");

    // getting the current value of autoEmbed
    const config = await pullServerConfigNoInsert(interaction.guild.id);

    // breaking if config is null
    if (!config) {
        console.log(`Error retrieving information about ${sha1sum(interaction.guild.id)}.`);
        return await interaction.reply({
            content: "There was an error retrieving information about your server.",
            ephemeral: true
        });
    }

    // user wants to display the current setting
    if (data === undefined) {
        // responding to caller
        return await interaction.reply({
            ephemeral: true,
            content: config.globalEmbed
                ? "Auto-embedding is set to true, any message in any channel that contains an iFunny link will be embedded."
                : 'Auto-embedding is set to false, any message in any channel that contains an iFunny link will be ignored. This can be overridden if there are any channels set via. "/config channels"',
        });
    }

    // user wants to set the configuration
    if (config.globalEmbed === data) {
        // breaking early here since there is no point changing true to true
        return await interaction.reply({
            content: `Set "auto-embed" to ${data}`,
            ephemeral: true,
        });
    }

    // user is actually changing the config, need to update the database
    const result = await executeQuery(interaction.guild.id, "config", "update", {
        data: {
            globalEmbed: data
        }
    });

    // evaluating the response
    if (result && result.globalEmbed === data) {
        return await interaction.reply({
            content: `Set "auto-embed" to ${data}`,
            ephemeral: true,
        });
    } else {
        console.error("Error during configAutoEmbed.\n", result);
        return await interaction.reply({
            content: `There was an error updating "auto-embed".`,
            ephemeral: true,
        });
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

    // breaking if config is null
    if (!config) {
        return await interaction.reply({
            content: "There was an error retrieving information about your server.",
            ephemeral: true
        });
    }

    // user wants to display the current setting
    if (!data) {
        // logging
        console.log(
            `Replying to user ${interaction.user.username} with the saved role ${config.role}.`
        );

        // if the role is "@everyone" this actually means "manage guild" & "admin"
        var message;
        if (!config.role || config.role === "1036130140977119322") {
            message =
                'Any user with "Manage Server" or "Administrator" can use this command.';
        } else {
            message = `Any user with "${
                interaction.guild.roles.resolve(config.role).name
            }" can use this command.`;
        }

        // responding to caller
        return await interaction.reply({
            ephemeral: true,
            content: message,
        });
    }

    // logging
    console.log(
        `Updating the saved role ${config.role} to ${data} for server ${sha1sum(interaction.guild.id)}.`
    );

    // mapping the id to the actual name to make more sense
    const oldRoleName = interaction.guild.roles.resolve(config.role).name;
    const newRoleName = interaction.guild.roles.resolve(data.id).name;

    // not applying unneeded changes
    if (config.role === data.id) {
        return await interaction.reply({
            content: `Changed ${oldRoleName} to ${newRoleName}`,
            ephemeral: true,
        });
    }

    // user is actually changing the role, we need to update the database
    const result = await executeQuery(interaction.guild.id, "config", "update", {
        data: {
            role: data.id
        }
    });

    // evaluating the response
    if (result && result.role === data.id) {
        return await interaction.reply({
            content: `Changed ${oldRoleName} to ${newRoleName}`,
            ephemeral: true,
        });
    } else {
        return await interaction.reply({
            content: `There was an error updating ${oldRoleName} to ${newRoleName}.`,
            ephemeral: true,
        });
    }
}

/**
 * this function shows, updates or sets the channels which autoembedding can occur in
 * @param {import("discord.js").Interaction} interaction the discord interaction
 */
async function configExportFormat(interaction) {
    // getting options
    const format = interaction.options.getString("format");

    // config
    const config = await pullServerConfigNoInsert(interaction.guild.id);

    // breaking if config is null
    if (!config) {
        return await interaction.reply({
            content: "There was an error retrieving information about your server.",
            ephemeral: true
        });
    }

    // if no action, list current export format 
    if (!format) {
        // returning the set export format
        const msg = `I am currently exporting images in "${config.exportFormat}" format.`;
        return await interaction.reply(msg);
    }

    // if the current format is the same as the desired format, don't do anything
    if (format === config.exportFormat) {
        return await interaction.reply({
            content: `Changed export format to ${format}.`,
            ephemeral: true,
        });
    }

    // logging
    console.log(`Updating image format of ${sha1sum(interaction.guild.id)} to ${format}.`);

    // user is actually changing the role, we need to update the database
    const result = await executeQuery(interaction.guild.id, "config", "update", {
        data: {
            exportFormat: format
        }
    });
    
    // evaluating the response
    if (result && result.exportFormat === format) {
        return await interaction.reply({
            content: `Changed export format to ${format}.`,
            ephemeral: true,
        });
    } else {
        return await interaction.reply({
            content: `There was an error updating ${config.exportFormat} to ${format}.`,
            ephemeral: true,
        });
    }
}

/**
 * this function shows, updates or sets the channels which autoembedding can occur in
 * @param {import("discord.js").Interaction} interaction the discord interaction
 */
async function configChannels(interaction) {
    // getting options
    const action = interaction.options.getString("action");
    const channel = interaction.options.getChannel("channel");

    // pulling all channels
    const channels = await prisma.channel.findMany({
        where: {
            server: sha1sum(interaction.guild.id),
        },
    });

    // if no action, list all channels
    if (!action && !channel) {
        // there are no saved channels
        if (channels.length === 0) {
            return await interaction.reply({
                content: "There are no saved channels for this server.",
                ephemeral: true,
            });
        }

        // there are one or more saved channels
        const humanReadableChannels = channels.map(obj => {
            return interaction.guild.channels.resolve(obj.channel);
        });
        const msg = `Here are the channels I have saved:\n${humanReadableChannels
            .toString()
            .replaceAll(",", "\n")}`;

        return await interaction.reply(msg);
    }

    // if no action and channel exists, reply with help message
    if (!action && channel) {
        return await interaction.reply({
            content: `Need an action for ${channel}.`,
            ephemeral: true,
        });
    }

    // if action exists and no channel, reply with help message
    if (action && !channel) {
        return await interaction.reply({
            content: `Need a channel to ${action}.`,
            ephemeral: true,
        });
    }

    // logging
    console.log(
        `${sha1sum(interaction.guild.id)} has ${channels.length} channels saved.`
    );

    if (!["add", "remove"].includes(action)) {
            return await interaction.reply({
                content: "You somehow managed to get here, good job!",
                ephemeral: true,
            });
    }

    // for string formatting
    const verb = action === "add" ? "sav" : "remov";

    /// testing if breaking early (adding a duplicate, removing a channel that isn't saved)
    const breakEarly = ((a) => {
        switch (a) {
            case "add":
                return channels.filter(obj => {
                    return obj.channel === channel.id;
                }).length > 0;
            case "remove":
                return channels.filter(obj => {
                    return obj.channel === channel.id;
                }).length === 0;
        }
    })(action);

    if (breakEarly) {
        // logging
        console.log(
            `${channel.id} was${action === "remove" ? "n't" : ""} found in the database, not ${verb}ing.`
        );

        // channel was found, breaking early
        return await interaction.reply({
            content: `Successfully ${verb}ed ${channel}.`,
            ephemeral: true,
        });
    } else {
        // logging
        console.log(`${channel.id} was${action === "add" ? "n't" : ""} found in the database, ${action === "add" ? "adding" : "removing"}.`);
    }

    // performing query
    const query = await (async (a) => {
        switch (a) {
            case "remove":
                return await executeQuery(interaction.guild.id, "channel", "delete", {
                    where: {
                        channel: channel.id
                    }
                });
            default:
                return await executeQuery(interaction.guild.id, "channel", "create", {
                    data: {
                        channel: channel.id,
                        server: sha1sum(interaction.guild.id),
                    },
                })
        }
    })(action);

    // asserting the result of the query
    if (
        query &&
        query.channel === channel.id
    ) {
        // logging
        console.log(`Successfully ${verb}ed ${channel.id} to the database.`);

        return await interaction.reply({
            content: `Successfully ${verb}ed ${channel}.`,
            ephemeral: true,
        });
    } else {
        // logging
        console.error("There was an error", query);

        return await interaction.reply({
            content: `There was an error ${verb}ing ${channel}.`,
            ephemeral: true,
        });
    }
}

/**
 * the handler function for the "Config" command
 * @param {import("discord.js").Interaction} interaction the discord interaction
 */
async function config(interaction) {
    // check if the server is saved in the database
    // if saved,
    //  continue
    // else,
    //  add the server to the database
    const config = await pullServerConfig(interaction.guild.id);

    // breaking if there's an error
    if (!config) {
        return await interaction.reply({
            content: "There was an error retrieving information about your server.",
            ephemeral: true
        });
    }

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
                // role name
                const roleName = interaction.guild.roles.resolve(
                    config.role
                ).name;

                // this looks fucking stupid
                console.log(
                    `User ${interaction.user.username} doesn't have the set role "${roleName}", they cannot execute Config.`
                );
                return interaction.reply({
                    ephemeral: true,
                    content: `You do not have the role ${roleName} and cannot execute this command.`,
                });
            }
        } else {
            // logging
            console.log(
                `There is no saved role for server ${config.server}. User ${interaction.user.username} cannot execute Config.`
            );
            return interaction.reply({
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
        `User ${interaction.user.username} has valid permissions, they can execute config option: ${option}.`
    );

    // choosing the right function handler based on the action
    switch (option) {
        case "autoembed":
            return await configAutoEmbed(interaction);
        case "channels":
            return await configChannels(interaction);
        case "role":
            return await configRole(interaction);
        case "file-format":
            return await configExportFormat(interaction);
        default:
            return interaction.reply({
                content: `Cannot configure unknown option: ${option}.`,
                ephemeral: true,
            });
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
                .addStringOption(option => {
                    return option
                        .setName("action")
                        .setDescription(
                            "Adds or removes a channel to the list."
                        )
                        .addChoices({ name: "add", value: "add" })
                        .addChoices({ name: "remove", value: "remove" });
                })
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
        })
        .addSubcommand(subcommand => {
            return subcommand
                .setName("file-format")
                .setDescription(
                    'Changes the output format of images. (default "png")'
                )
                .addStringOption(option => {
                    // setting up the option
                    option
                        .setName("format")
                        .setDescription(
                            "List of preset image formats."
                        );

                    // adding all the options
                    imageExportFormats.forEach(format => {
                        option.addChoices({ name: format, value: format });
                    });

                    // returning the option
                    return option;
                })
        }),
    execute: config,
};

export default Config;
