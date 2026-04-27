load("@rules_python//python:defs.bzl", "py_binary", "py_library", "py_test")
load(":cmake_to_bazel.bzl", "cmake_to_bazel")

py_library(
    name = "ast_nodes",
    srcs = ["ast_nodes.py"],
    imports = [".."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "ast_generator",
    srcs = ["ast_generator.py"],
    deps = [":ast_nodes"],
    imports = [".."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "bazel_emitter",
    srcs = ["bazel_emitter.py"],
    deps = [":ast_nodes"],
    imports = [".."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "cmake_to_bazel_lib",
    srcs = [
        "__init__.py",
        "file_api_spike.py",
        "main.py",
    ],
    deps = [
        ":ast_generator",
        ":bazel_emitter",
        "//cmake_to_bazel/parsers:cmake_parser",
    ],
    imports = [".."],
    visibility = ["//visibility:public"],
)

py_binary(
    name = "cli",
    srcs = ["cli.py"],
    deps = [":cmake_to_bazel_lib"],
    imports = [".."],
    visibility = ["//visibility:public"],
)

py_test(
    name = "ast_nodes_tests",
    srcs = ["ast_nodes_tests.py"],
    deps = [":ast_nodes"],
    imports = [".."],
    size = "small",
)

py_test(
    name = "ast_generator_tests",
    srcs = ["ast_generator_tests.py"],
    deps = [
        ":ast_generator",
        ":ast_nodes",
    ],
    imports = [".."],
    size = "small",
)

py_test(
    name = "e2e_transpile_tests",
    srcs = ["e2e_transpile_tests.py"],
    data = ["//:e2e_transpile_data"],
    deps = [":cmake_to_bazel_lib"],
    imports = [".."],
    size = "small",
)

py_test(
    name = "file_api_spike_tests",
    srcs = ["file_api_spike_tests.py"],
    data = glob(["testdata/**"]),
    deps = [":cmake_to_bazel_lib"],
    imports = [".."],
    size = "small",
)
