load("@gazelle//:def.bzl", "gazelle")
load("@npm//:defs.bzl", "npm_link_all_packages")

exports_files(["shell.nix", ".envrc"])

gazelle(name = "gazelle")

alias(
    name = "funcaptcha",
    actual = "@com_github_acheong08_funcaptcha//cmd/api",
)

alias(
    name = "chatgptproxy",
    actual = "@com_github_acheong08_chatgptproxy//:ChatGPTProxy",
)

npm_link_all_packages(name = "node_modules")
