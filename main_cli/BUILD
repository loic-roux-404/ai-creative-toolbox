load("@rules_python//python:defs.bzl", "py_binary", "py_test")

py_binary(
    name = "main_cli",
    main = "__main__.py",
    srcs = ["__main__.py"],
    imports = ["."],
    deps = [
        "//core_automation:core_automation",
    ]
)

[py_test(
    name = "main_cli_" + f[:-3],
    size = "small",
    srcs = [f],
    main = f,
    deps = ["//main_cli:main_cli"]
) for f in ["tests/test_main.py", "tests/conftest.py"]]
