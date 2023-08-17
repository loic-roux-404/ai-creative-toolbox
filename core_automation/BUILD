load("@rules_python//python:defs.bzl", "py_library")
load("@pip//:requirements.bzl", "requirement")

py_library(
    name = "core_automation",
    srcs = glob(["*.py", "**/*.py"]),
    deps = [
        requirement("google-api-python-client"),
        requirement("google-auth-httplib2"),
        requirement("google-auth-oauthlib"),
        requirement("beautifulsoup4"),
        requirement("gradio_client"),
        requirement("html2text"),
        requirement("opencv-python"),
        requirement("python-dotenv"),
        requirement("revChatGPT"),
        requirement("split_markdown4gpt"),
        requirement("tesserocr"),
        requirement("transformers"),
        requirement("wand"),
    ],
    visibility = ["//main_cli:__pkg__"]
)
