import puppeteer from "puppeteer";
import { scrollPageToBottom } from "puppeteer-autoscroll-down";
import { Page } from "puppeteer";
import { Browser } from "puppeteer";

const DEFAULT_ARGS = ["--no-sandbox", "--disable-setuid-sandbox"];
const DEFAULT_USER_AGENT =
  "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36";
const waitUntil = "networkidle0";

/**
 * @typedef {Object} Config
 * @property {string[]} courseListUrls
 * @property {string} baseUrl
 * @property {string} email
 * @property {string} password
 * @property {boolean} headless
 */

/**
 * Validate config keys
 * @param {object} config
 * @param {Array} requiredKeys
 * @returns
 */
function validateConfigKeys(config, requiredKeys) {
  if (requiredKeys.every((key) => key in config)) return;

  throw new Error(
    `Config must contain the following keys: ${requiredKeys.join(", ")}`
  );
}

/**
 * login
 * @param {Browser} browser
 * @param {Config} config
 * @returns
 */
async function login(browser, config) {
  validateConfigKeys(config, ["baseUrl", "email", "password"]);
  const page = await browser.newPage();
  await page.setUserAgent(DEFAULT_USER_AGENT);

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
  await scrollPageToBottom(page, { size: 500, delay: 250 });
}

/**
 * goToCourses
 * @param {Page} page
 * @param {Config} config
 * @param {courseListUrl} config
 */
async function goToCourses({ page, config, courseListUrl }) {
  validateConfigKeys(config, ["baseUrl"]);
  await page.goto(new URL(courseListUrl, config.baseUrl).href, {
    waitUntil: "domcontentloaded",
  });
  await page.waitForSelector('[class^="CardLarge---title"]');
}

/**
 * getCourses
 * @param {Browser} browser
 * @param {Config} config
 * @returns
 */
async function getCourses({ browser, config, courseListUrl }) {
  const page = await browser.newPage();
  await page.setUserAgent(DEFAULT_USER_AGENT);
  await page.setCacheEnabled(true);

  await goToCourses({ page, config, courseListUrl });
  await scrollToFooter(page);
  // Get all course cards
  const courseCards = await page.$$('[class^="CardLarge---titleLink"]');

  console.info("Found", courseCards.length, "courses");

  const coursesUrl = (
    await Promise.all(
      courseCards.map(async (link) => await link.evaluate((el) => el.href))
    )
  ).filter((url) => url.includes("courses/"));

  let urls = [];

  for (const courseUrl of coursesUrl) {
    await page.goto(courseUrl + "?tab=resources", { waitUntil });
    await scrollToFooter(page);
    console.info("Extracting transcript of", courseUrl);

    try {
      const transcriptLink = await page.waitForSelector(
        '[data-marker="sendUTSEvent"]',
        { timeout: 5000 }
      );
      urls = urls.concat(await transcriptLink.evaluate((el) => el.href));
    } catch (err) {
      console.warn("Error during process of ", courseUrl);
      console.debug(err)
    }
  }

  return urls;
}

/**
 * Start process
 * @param {Config} config
 */
export default async function (config) {
  validateConfigKeys(config, ["courseListUrls"]);

  const browser = await puppeteer.launch({
    headless: "headless" in config ? config.headless : false,
    args: DEFAULT_ARGS,
  });

  await login(browser, config);
  let urls = []
  for (const courseListUrl of config.courseListUrls) {
    console.info("Extracting courses from playblist :", courseListUrl);
    urls = urls.concat(await getCourses({ browser, config, courseListUrl }));
  }

  console.info(JSON.stringify({ urls }));

  await browser.close();
}
