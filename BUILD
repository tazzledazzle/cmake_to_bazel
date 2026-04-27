load("//cmake_to_bazel:cmake_to_bazel.bzl", "cmake_to_bazel")

exports_files([
    "requirements.txt",
    "testfiles/CMakeLists.txt",
])

filegroup(
    name = "e2e_transpile_data",
    srcs = [
        "//docs/examples/simple:BUILD.expected",
        "//docs/examples/simple:CMakeLists.txt",
    ] + glob(["testfiles/**"]),
    visibility = ["//visibility:public"],
)

alias(
    name = "main",
    actual = "//cmake_to_bazel:cli",
)

cmake_to_bazel(
    name = "generate_bazel_build",
    cmake_file = "//:testfiles/CMakeLists.txt",
)
