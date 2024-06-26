# cmake_to_bazel/BUILD

load("//cmake_to_bazel:cmake_to_bazel.bzl", "cmake_to_bazel")

py_binary(
    name = "main",
    srcs = ["parsers/cmake_parser.py"],
)

cmake_to_bazel(
    name = "generate_bazel_build",
    cmake_file = "testfiles/CMakeLists.txt",
    output_dir = "test-output",
)
