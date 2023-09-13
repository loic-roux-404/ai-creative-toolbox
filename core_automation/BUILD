load("@pip//:requirements.bzl", "requirement")
load("@rules_python//python:defs.bzl", "py_library")

# exports_files(['shell.nix'])

py_library(
    name = "core_automation",
    srcs = glob([
        "*.py",
        "**/*.py",
    ]),
    visibility = ["//main_cli:__pkg__"],
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
        requirement("jinja2"),
        requirement("pydantic"),
    ],
)

py_test(
    name = "core_automation_test",
    size = "small",
    srcs = ["pytest-start.py"],
    args = [
        "--capture=no",
        "--ignore=external",
    ],
    main = "pytest-start.py",
    deps = [
        ":core_automation",
        requirement("pytest"),
    ],
)
