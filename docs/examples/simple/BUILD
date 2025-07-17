# Generated from CMakeLists.txt by cmake_to_bazel transpiler

cc_library(
    name = "SimpleLib",
    srcs = ["src/lib.cpp"],
    includes = ["include"],
)

cc_binary(
    name = "SimpleApp",
    srcs = [
        "src/main.cpp",
        "src/helper.cpp",
    ],
    includes = ["include"],
    deps = [":SimpleLib"],
)