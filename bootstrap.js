// Require the necessary discord.js classes
import { REST, Routes, Client, GatewayIntentBits } from "discord.js";
import config from "./config.json" assert { type: "json" };
import User from "./commands/user.js";
import About from "./commands/about.js";
import Post from "./commands/post.js";
import Help from "./commands/help.js";
import Config from "./commands/config.js";
import Hash from "./commands/hashfiles.js";
import { isValidiFunnyLink } from "./utils/utils.js";
import extractPost from "./utils/extractpost.js";
import { pullServerConfig, pullChannels } from "./utils/db.js";

// creating a list of valid commands used by the bot
const Commands = [Post, User, About, Help, Hash, Config];

// Create a new client instance
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
    ],
});

// the list of all bot commands
client.commands = Commands;

// establishing a rest connection to discord
const rest = new REST({ version: "10" }).setToken(config.token);

/**
 * @callback _MessageCreate
 * @param {import ("discord.js").Message} message the message sent
 * @returns {Promise<void>}
 *
 * @callback _InteractionCreate
 * @param {import ("discord.js").Interaction} interaction the interaction
 * @returns {Promise<void>}
 */

/**
 * @namespace Bootstrap
 */

const dev = {
    ClientReady: c => {
        console.log(`Ready! Logged in as ${c.user.tag}`);

        // for maintenance
        client.user.setActivity("Down for maintenance!");
        client.user.setStatus("dnd");
    },
    /**
     * @memberof Bootstrap
     * @method MessageCreate The handler for Events.MessageCreate
     * @type {_MessageCreate}
     */
    MessageCreate: async message => {
        // ignoring messages that aren't from the development server
        if (message.guild.id !== config.guildId) return;

        // don't react to the bot sending messages
        if (message.author == client.user.id) return;

        // querying the prisma db to see if this server has "globalEmbed" enabled
        const serverConfig = await pullServerConfig(message.guild.id);

        // if global config is disabled, stop function
        if (serverConfig.globalEmbed === false) {
            // global embed is disabled, aborting
            console.log(
                `Server ${message.guild.id} has global embed disabled, checking for a saved channel.`
            );

            // if the interaction was in a saved channel, allow
            const channels = await pullChannels(message.guild.id);

            // there are no saved channels
            if (channels.length === 0) {
                console.log(
                    `There are no saved channels for ${message.guild.id}, aborting auto-embed.`
                );
                return;
            }

            // there are one or more saved channels
            console.log(
                `${message.guild.id} has one or more saved channels, checking if the interaction's channel is valid.`
            );

            if (
                channels.filter(obj => {
                    return obj.channel === message.channel.id;
                }).length === 0
            ) {
                console.log(
                    `The message was sent in a channel that doesn't have auto-embed enabled, aborting.`
                );
                return;
            }

            // logging
            console.log(
                `Allowing auto-embed in channel ${message.channel.id}.`
            );
        }

        // automatically embed a post if there is a valid ifunny link in it
        if (isValidiFunnyLink(message.content)) {
            // logging
            console.log(`Auto-embedding content from ${message.content}`);

            // extracting the post in the message
            extractPost(
                message.content,
                resolve => {
                    message.reply(resolve);
                },
                error => {
                    console.log(
                        `There was an error during auto embed: ${error}`
                    );
                    return;
                }
            );
        }
    },
    /**
     * @memberof Bootstrap
     * @method InteractionCreate The handler for Events.InteractionCreate
     * @type {_InteractionCreate}
     */
    InteractionCreate: async interaction => {
        if (!interaction.isChatInputCommand()) return;

        // filtering through the commands to find the requested command
        const [command] = client.commands.filter(command => {
            return command.data.name === interaction.commandName;
        });

        // just in case the command that was called is undefined
        if (command === undefined) {
            const msg = `You somehow tried to call an undefined command "${interaction.commandName}" Good job!`;
            await interaction.reply({ content: msg, ephemeral: true });
            return;
        }

        // trying to execute the command
        try {
            // logging
            console.log(
                `The command ${interaction.commandName} was executed by ${interaction.member.user.username}. ` +
                    `With args:`
            );
            interaction.options.data.map(U => {
                console.log(U);
            });

            // executing the command
            await command.execute(interaction);
        } catch (error) {
            // something went wrong executing this command
            console.error(error);
            await interaction.reply({
                content: `An error occurred using ${interaction.commandName}`,
                ephemeral: true,
            });
        }
    },
    Put: async payload => {
        return await rest.put(
            Routes.applicationGuildCommands(config.clientId, config.guildId),
            { body: payload }
        );
    },
};

const prod = {
    ClientReady: c => {
        console.log(`Ready! Logged in as ${c.user.tag}`);

        // setting the activity
        client.user.setActivity("Use /about for the bot!");
    },
    /**
     * @memberof Bootstrap
     * @method MessageCreate The handler for Events.MessageCreate
     * @type {_MessageCreate}
     */
    MessageCreate: async message => {
        // don't react to the bot sending messages
        if (message.author == client.user.id) return;

        // automatically embed a post if there is a valid ifunny link in it
        if (isValidiFunnyLink(message.content)) {
            // logging
            console.log(`Embedding content from ${message.content}`);

            // extracting the post in the message
            extractPost(
                message.content,
                resolve => {
                    message.reply(resolve);
                },
                _ => {
                    return;
                }
            );
        }
    },
    /**
     * @memberof Bootstrap
     * @method InteractionCreate The handler for Events.InteractionCreate
     * @type {_InteractionCreate}
     */
    InteractionCreate: async interaction => {
        if (!interaction.isChatInputCommand()) return;

        // filtering through the commands to find the requested command
        const [command] = client.commands.filter(command => {
            return command.data.name === interaction.commandName;
        });

        // just in case the command that was called is undefined
        if (command === undefined) {
            const msg = `You somehow tried to call an undefined command "${interaction.commandName}." Good job!`;
            console.log(msg);
            await interaction.reply({ content: msg, ephemeral: true });
            return;
        }

        // trying to execute the command
        try {
            // logging
            console.log(
                `The command ${interaction.commandName} was executed by ${interaction.member.user.username}.`
            );

            // executing the command
            await command.execute(interaction);
        } catch (error) {
            // something went wrong executing this command
            console.error(error);
            await interaction.reply({
                content: "There was an error while executing this command!",
                ephemeral: true,
            });
        }
    },
    Put: async payload => {
        // establishing a rest connection to discord
        const rest = new REST({ version: "10" }).setToken(config.token);

        return await rest.put(Routes.applicationCommands(config.clientId), {
            body: payload,
        });
    },
};

export { client as Client, dev, prod, Commands };
