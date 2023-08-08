import { PrismaClient } from "@prisma/client";

// the connection to the database
const prisma = new PrismaClient();

async function pullChannels(id) {
    // logging
    console.log(`Fetching all channels from ${id}.`);

    // pulling all the channels from the channels table
    return await prisma.channel.findMany({
        where: {
            server: id
        }
    });
}

/**
 * this function inserts a server of `id` into the database
 * @param {String} id the id of the server
 * @returns the result of the insert
 */
async function insertServerToDB(id) {
    // logging
    console.log(`Inserting the server ${id} into the database.`);

    // adding the server to the database
    return await prisma.config.create({
        data: {
            server: id,
            globalEmbed: true,
            role: "",
        },
    });
}

/**
 * this function retrieves the configuration of a server without inserting it into the database
 * @param {String} id the id of the server
 * @param {Boolean} verbose if true, print logging message
 * @returns the configuration of the server
 */
async function pullServerConfigNoInsert(id, verbose = true) {
    // logging
    if (verbose)
        console.log(
            `Pulling the configuration of server ${id} from the database.`
        );

    // pulling the server config without inserting the server into the database
    return await prisma.config.findFirst({
        where: {
            server: id,
        },
    });
}

/**
 * this function retrieves the configuration of a server and inserts the server
 * into the database if not exists
 * @param {String} id the id of the server
 * @returns the configuration of the server
 */
async function pullServerConfig(id) {
    // pulling the server config and inserting the server if not exists
    const config = await pullServerConfigNoInsert(id, false);

    // inserting server into DB if not exists
    if (config == null) {
        // logging
        console.log(`Configuration for server ${id} doesn't exist, creating.`);

        // inserting the server into the database
        const result = await insertServerToDB(id);

        // if valid insertion
        if (result && result.count == 1) {
            console.log(
                `Successfully added server ${id} to the "Config" table.`
            );
        } else {
            console.error(`Couldn't add server ${id} to the "Config" table.`);
            console.error(result);
        }

        // returning with the new config
        return await pullServerConfigNoInsert(id, false);
    }

    // don't need to pull the configuration twice if there's already config available
    return config;
}

export { prisma, insertServerToDB, pullServerConfig, pullServerConfigNoInsert, pullChannels };
