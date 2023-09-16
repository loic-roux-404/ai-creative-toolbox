load("@rules_python//python:defs.bzl", "py_binary", "py_test")

py_binary(
    name = "main_cli",
    srcs = ["__main__.py"],
    imports = ["."],
    main = "__main__.py",
    deps = ["//core_automation"],
)

[py_test(
    name = "main_cli_" + f[:-3],
    size = "small",
    srcs = [f],
    main = f,
    deps = ["//main_cli"],
) for f in [
    "tests/test_main.py",
    "tests/conftest.py",
]]
