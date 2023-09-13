load("@gazelle//:def.bzl", "gazelle")
load("@npm//:defs.bzl", "npm_link_all_packages")
load("@rules_go//go:def.bzl", "go_binary")

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

filegroup(
    name = "environment",
    srcs = [".env"],
    visibility = ["//visibility:public"],
)
