
load("@rules_python//python:defs.bzl", "py_library", "py_test")

py_library(
    name = "cmake_parser",
    srcs = ["cmake_parser.py"],
    visibility = ["//visibility:public"],
)

py_test(
    name = "cmake_parser_tests",
    srcs = ["cmake_parser_tests.py"],
    deps = [
        ":cmake_parser",
        "@pip_deps//pypi__pytest",
    ],
)
