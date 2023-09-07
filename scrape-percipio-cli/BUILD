load("@aspect_rules_js//js:defs.bzl", "js_binary")
load("@npm//:defs.bzl", "npm_link_all_packages")

npm_link_all_packages(name = "node_modules")

js_binary(
    name = "scrape-percipio-cli",
    data = ["//scrape-percipio"],
    entry_point = "cli.mjs",
)
