import { parseArgs } from "node:util";
import fs from'fs'
import scrapePercipio from "../scrape-percipio/index.js";

async function main() {

    const {
        values: { config },
    } = parseArgs({
        options: {
        config: {
            type: "string",
            short: "c",
        },
        },
    });

    try {
        const configParsed = await JSON.parse(fs.readFileSync(config, 'utf8'))
        scrapePercipio(configParsed);
    } catch (err) {
        console.error('Error during process', err);
    };
}

main();
