import puppeteer from "puppeteer";
import { scrollPageToBottom } from "puppeteer-autoscroll-down";
import { Page } from "puppeteer";
import { Browser } from "puppeteer";

const DEFAULT_ARGS = ["--no-sandbox", "--disable-setuid-sandbox"];
const DEFAULT_USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'

function validateConfigKeys(config, requiredKeys) {
  if (requiredKeys.every((key) => key in config)) return;

  throw new Error(
    `Config must contain the following keys: ${requiredKeys.join(", ")}`
  );
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

/**
 * scrollToFooter
 * @param {Page} page
 */
async function scrollToFooter(page) {
  await page.waitForSelector('[class^="Footer---root"]');
  await scrollPageToBottom(page, { size: 500, delay: 250 })
}

/**
 * goToCourses
 * @param {Page} page
 * @param {object} config
 */
async function goToCourses(page, config) {
  validateConfigKeys(config, ["baseUrl", "courseListUrl"]);
  await page.goto(
    new URL(config.courseListUrl, config.baseUrl).href,
    { waitUntil: "domcontentloaded" }
  );
  await page.waitForSelector('[class^="CardLarge---title"]');
  await scrollToFooter(page);
}

/**
 * getCourses
 * @param {Browser} browser
 * @param {object} config
 * @returns
 */
async function getCourses(browser, config) {
  const page = await browser.newPage();
  page.setUserAgent(DEFAULT_USER_AGENT);
  await goToCourses(page, config);
  // Get all course cards
  const courseCards = await page.$$('[class^="CardLarge---titleLink"]');

  console.info("Found", courseCards.length, "courses");

  const coursesUrl = (
    await Promise.all(
      courseCards.map(async (link) => await link.evaluate((el) => el.href))
    )
  ).filter((url) => url.includes("courses/"));

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
      await goToCourses(page, config);
      urls.push(url);
    }

    // Navigate back to the list (if it's required)
    await goToCourses(page, config);
  }

  console.info(JSON.stringify({ urls }));

  return urls;
}

export default async function (config) {
  const browser = await puppeteer.launch({
    headless: "headless" in config ? config.headless : false,
    args: DEFAULT_ARGS,
  });
  await login(browser, config);
  await getCourses(browser, config);

  await browser.close();
}
