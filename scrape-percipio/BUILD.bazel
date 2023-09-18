load("@aspect_rules_js//js:defs.bzl", "js_library")
load("@npm//:defs.bzl", "npm_link_all_packages")

npm_link_all_packages(name = "node_modules")

js_library(
    name = "scrape-percipio",
    srcs = [
        "index.js",
        "package.json",
    ],
    data = [
        "//scrape-percipio:node_modules/puppeteer",
        "//scrape-percipio:node_modules/puppeteer-autoscroll-down",
    ],
    visibility = ["//scrape-percipio-cli:__pkg__"],
)
