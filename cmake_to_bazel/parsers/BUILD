
load("@rules_python//python:defs.bzl", "py_library", "py_test")

py_library(
    name = "cmake_parser",
    srcs = ["cmake_parser.py"],
)

py_test(
    name = "cmake_parser_test",
    srcs = ["cmake_parser_test.py"],
    deps = [
        ":cmake_parser",
        "@pip_deps//pypi__pytest",
    ],
)

