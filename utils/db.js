import { PrismaClient } from "@prisma/client";
import Crypto from "node:crypto";

// the connection to the database
const prisma = (_ => {
    try {
        const __prisma = new PrismaClient();
        return __prisma
    } catch (error) {
        console.error("Could not instantiate the prisma client.");
        return undefined
    }
})();

// returns the sha1 digest of some input
const sha1sum = input => {
    return Crypto.createHash("sha1").update(input).digest("hex");
};

// a simple shorthand to log error
function prismaErrorHandler(reason) {
    if (reason.code === "P2021") {
        console.error("WARNING: RUNNING BOT WITHOUT LIVE DATABASE\n", reason);
    } else {
        console.error("WARNING: UNKNOWN ERROR\n", reason);
    }
    return undefined;
}

/**
 * this function pulls all of the channel ids that are associated with the server
 * @param {String} id the id of the server
 * @returns a list of channels
 */
async function pullChannels(id) {
    // early aborting
    if (!prisma) {
        return prismaErrorHandler({ reason: "Couldn't instantiate prisma client." });
    }

    // hashing
    const hash = sha1sum(id);

    // logging
    console.log(`Fetching all channels from ${hash}.`);

    // pulling all the channels from the channels table
    return prisma.channel
        .findMany({
            where: {
                server: hash,
            },
        })
        .then(result => {
            return result;
        })
        .catch(prismaErrorHandler);
}

/**
 * this function inserts a server of `id` into the database
 * @param {String} id the id of the server
 * @returns the result of the insert
 */
async function insertServerToDB(id) {
    // early aborting
    if (!prisma) {
        return prismaErrorHandler({ reason: "Couldn't instantiate prisma client." });
    }

    // hashing
    const hash = sha1sum(id);

    // logging
    console.log(`Inserting the server ${hash} into the database.`);

    // adding the server to the database
    return prisma.config
        .create({
            data: {
                server: hash,
                globalEmbed: true,
                role: "",
                exportFormat: "png",
            },
        })
        .then(result => {
            return result;
        })
        .catch(prismaErrorHandler);
}

/**
 * this function retrieves the configuration of a server without inserting it into the database
 * @param {String} id the id of the server
 * @param {Boolean} verbose if true, print logging message
 * @returns the configuration of the server
 */
async function pullServerConfigNoInsert(id) {
    // early aborting
    if (!prisma) {
        return prismaErrorHandler({ reason: "Couldn't instantiate prisma client." });
    }

    // hashing
    const hash = sha1sum(id);

    // pulling the server config without inserting the server into the database
    return prisma.config
        .findFirst({
            where: {
                server: hash,
            },
        })
        .then(result => {
            return result;
        })
        .catch(prismaErrorHandler);
}

/**
 * this function retrieves the configuration of a server and inserts the server
 * into the database if not exists
 * @param {String} id the id of the server
 * @returns the configuration of the server
 */
async function pullServerConfig(id) {
    // early aborting
    if (!prisma) {
        return prismaErrorHandler({ reason: "Couldn't instantiate prisma client." });
    }

    // hashing
    const server_hash = sha1sum(id);

    // pulling the server config and inserting the server if not exists
    const config = await pullServerConfigNoInsert(id);

    // inserting server into DB if not exists
    if (!config) {
        // logging
        console.log(
            `Configuration for server ${server_hash} doesn't exist, creating.`
        );

        // inserting the server into the database
        const result = await insertServerToDB(id);

        // if valid insertion
        if (result && result.server === server_hash) {
            console.log(
                `Successfully added server ${server_hash} to the "Config" table.`
            );
        } else {
            console.error(
                `Couldn't add server ${server_hash} to the "Config" table.`
            );
            console.error("Reason:", result);
            return undefined;
        }

        // returning with the new config
        return await pullServerConfigNoInsert(id);
    }

    // don't need to pull the configuration twice if there's already config available
    return config;
}

async function executeQuery(server, table, action, query) {
    // early aborting
    if (!prisma) {
        return prismaErrorHandler({ reason: "Couldn't instantiate prisma client." });
    }

    // copying the query
    const __q = query;

    // passing in the server hash
    if (__q.data && !Object.keys(__q.data).includes("server")) {
        if (__q.where) {
            __q.where.server = sha1sum(server);
        } else {
            __q.where = { server: sha1sum(server) };
        }
    }
    // run query against table
    return await prisma[table][action](query)
        .then(result => {
            return result;
        })
        .catch(prismaErrorHandler);
}

export {
    prisma,
    insertServerToDB,
    pullServerConfig,
    pullServerConfigNoInsert,
    pullChannels,
    executeQuery,
    sha1sum,
};
