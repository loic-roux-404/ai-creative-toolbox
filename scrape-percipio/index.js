import puppeteer from "puppeteer";

function validateConfigKeys(config, requiredKeys) {
    if (!requiredKeys.every(key => key in config)) {
        throw new Error(
            `Config must contain the following keys: ${requiredKeys.join(
                ", "
            )}`
        );
    };
}

async function login(browser, config) {
    validateConfigKeys(config, ["baseUrl", "email", "password"]);
    const page = await browser.newPage();

    await page.goto(`${config.baseUrl}/login?state=%2F#/`);

    await page.waitForSelector('[class^="Login---container"]');

    // Fill in the login details
    await page.type("#loginName", config.email);

    await page.click('button[type="button"]');

    await page.type("#password", config.password);

    // Click login button
    await page.click('button[type="submit"]');

    // Wait for navigation to complete
    await page.waitForNavigation();

    await page.waitForSelector('[class^="ProfilePicture"]');
}

async function goToCourses(page, config) {
    validateConfigKeys(config, ["baseUrl", "courseListUrl"]);
    await page.goto(`${config.baseUrl}/${config.courseListUrl}`);

    await page.waitForSelector('[class^="CardLarge---title"]');
}

async function getCourses(browser) {
    const page = await browser.newPage();
    await goToCourses(page);
    // Get all course cards
    const courseCards = await page.$$('a[data-marker="openCourse"]');


    const coursesUrl = await Promise.all(courseCards.map(async link => await link.evaluate((el) => el.href)))
    const urls = [];

    for (const courseUrl of coursesUrl) {
        console.log("Extracting transcript of", courseUrl);

        // Ensure that the navigation after the click (if there's any) has completed
        await page.goto(courseUrl + "?tab=resources");

        const transcriptElementSelector = '[class^="ContentItem---link"]';

        await page.waitForSelector(transcriptElementSelector);

        // Extract URL
        const linkElement = await page.$(transcriptElementSelector);
        if (linkElement) {
            const url = await linkElement.evaluate((el) => el.href);
            await goToCourses(page);
            urls.push(url);
        }

        // Navigate back to the list (if it's required)
        await goToCourses(page);
    }

    console.log(urls);

    return urls;
}

export default async function(config) {
    const browser = await puppeteer.launch({ headless: false });
    await login(browser, config);
    await getCourses(browser);

    await browser.close();
}
