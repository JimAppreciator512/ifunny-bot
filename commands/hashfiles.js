import path from "node:path/posix";
import fs from "node:fs";
import { execSync } from "node:child_process";
import { createHash } from "node:crypto";
import { SlashCommandBuilder } from "discord.js";

const restricted = ["config.json", ".git", "node_modules"];

async function hash(interaction) {
    // deferring the reply
    await interaction.deferReply();

    // recursive file finding function
    function base(dir, done) {
        var results = [];

        fs.readdirSync(dir).forEach(file => {
            // not hashing certain files nor directories
            if (restricted.includes(file)) {
                return;
            }

            /// stating the file to figure out if it's a dir or not
            const stat = fs.statSync(path.resolve(dir, file));

            // if directory, walk, else hash
            if (stat && stat.isDirectory()) {
                // walk directory
                base(path.resolve(dir, file), (_, res) => {
                    res.forEach(f => {
                        results.push({
                            name: `${file}/${f.name}`,
                            hash: f.hash,
                        });
                    });
                });
            } else {
                // hash the file
                const md5sum = createHash("md5")
                    .update(fs.readFileSync(path.resolve(dir, file)))
                    .digest("hex");

                // logging
                console.log(`${md5sum}: ${path.resolve(dir, file)}`);

                // and push it to the array
                results.push({
                    name: path.basename(file),
                    hash: md5sum,
                });
            }
        });

        // returning the files
        return done(null, results);
    }

    // calling the recursive file hashing command
    return base(process.cwd(), (_, res) => {
        // pulling the latest git commit
        const output = execSync(
            "git log --oneline | head -n 1 | tr -d \"\n\"", // fuck dealing with buffers dude
            { cwd: process.cwd() }
        );

        // forming the string to return
        var str = `Latest git commit: \`${output}\`\nMD5 Hashes\n\`\`\`\n`;

        // formatting the files into a string
        for (const file of res) {
            str = str.concat(`${file.hash}: ${file.name}\n`);
        }
        str = str.concat("```");

        // replying with the data
        return interaction.editReply(str);
    });
}

const Hash = {
    data: new SlashCommandBuilder()
        .setName("hash")
        .setDescription("Hash all the files the bot is using."),
    execute: hash,
};

export default Hash;
