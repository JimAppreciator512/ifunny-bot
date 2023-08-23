import { PrismaClient } from "@prisma/client";
import Crypto from "node:crypto";

// the connection to the database
const prisma = new PrismaClient();

// returns the sha1 digest of some input
const sha1sum = input => {
    return Crypto.createHash("sha1").update(input).digest("hex");
};

/**
 * this function pulls all of the channel ids that are associated with the server
 * @param {String} id the id of the server
 * @returns a list of channels
 */
async function pullChannels(id) {
    // hashing
    const hash = sha1sum(id);

    // logging
    console.log(`Fetching all channels from ${hash}.`);

    // pulling all the channels from the channels table
    return await prisma.channel.findMany({
        where: {
            server: hash,
        },
    });
}

/**
 * this function inserts a server of `id` into the database
 * @param {String} id the id of the server
 * @returns the result of the insert
 */
async function insertServerToDB(id) {
    // hashing
    const hash = sha1sum(id);

    // logging
    console.log(`Inserting the server ${hash} into the database.`);

    // adding the server to the database
    return await prisma.config.create({
        data: {
            server: hash,
            globalEmbed: true,
            role: "",
            exportFormat: "png"
        },
    });
}

/**
 * this function retrieves the configuration of a server without inserting it into the database
 * @param {String} id the id of the server
 * @param {Boolean} verbose if true, print logging message
 * @returns the configuration of the server
 */
async function pullServerConfigNoInsert(id) {
    // hashing
    const hash = sha1sum(id);

    // pulling the server config without inserting the server into the database
    return await prisma.config.findFirst({
        where: {
            server: hash,
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
    // hashing
    const server_hash = sha1sum(id);

    // pulling the server config and inserting the server if not exists
    const config = await pullServerConfigNoInsert(id);

    // inserting server into DB if not exists
    if (config == null) {
        // logging
        console.log(
            `Configuration for server ${server_hash} doesn't exist, creating.`
        );

        // inserting the server into the database
        const result = await insertServerToDB(id);

        // if valid insertion
        if (result && result.server === undefined) {
            console.log(
                `Successfully added server ${server_hash} to the "Config" table.`
            );
        } else {
            console.error(`Couldn't add server ${server_hash} to the "Config" table.`);
            console.error("Reason:", result);
        }

        // returning with the new config
        return await pullServerConfigNoInsert(id);
    }

    // don't need to pull the configuration twice if there's already config available
    return config;
}

export {
    prisma,
    insertServerToDB,
    pullServerConfig,
    pullServerConfigNoInsert,
    pullChannels,
    sha1sum
};
