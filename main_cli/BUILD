load("@rules_python//python:defs.bzl", "py_binary", "py_test")
load("//main_cli:imagick.bzl", "imagick")

py_binary(
    name = "main_cli",
    main = "__main__.py",
    srcs = ["__main__.py"],
    imports = ["."],
    deps = [
        "//core_automation:core_automation",
    ]
)

py_test(
    name = "main_cli_test",
    size = "small",
    srcs = ["tests/test_main.py", "tests/conftest.py"],
    main = "tests/test_main.py",
    deps = ["//main_cli:main_cli"],
    env = {
        "PATH": imagick(),
    }
)
