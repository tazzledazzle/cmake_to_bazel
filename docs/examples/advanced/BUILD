# Generated from CMakeLists.txt by cmake_to_bazel transpiler

# Global variables
SOURCES = [
    "src/main.cpp",
    "src/helper.cpp",
    "src/utils.cpp",
]

LIB_SOURCES = [
    "src/lib.cpp",
    "src/lib_utils.cpp",
]

# Library target
cc_library(
    name = "AdvancedLib",
    srcs = LIB_SOURCES,
    includes = [
        "include",
        "third_party/include",
        "src/internal",
    ],
    copts = [
        "-Wall",
        "-Werror",
        "-DVERSION=\\\"1.0.0\\\"",
        "-DENABLE_TESTS",
    ],
)

# Main executable
cc_binary(
    name = "AdvancedApp",
    srcs = SOURCES,
    includes = [
        "include",
        "third_party/include",
    ],
    deps = [
        ":AdvancedLib",
    ],
    linkopts = [
        "-lpthread",
        "-ldl",
    ],
    defines = [
        "VERSION=\\\"1.0.0\\\"",
        "ENABLE_TESTS",
    ],
)

# Test executable
cc_test(
    name = "AdvancedTests",
    srcs = [
        "tests/test_main.cpp",
        "tests/test_lib.cpp",
    ],
    includes = [
        "include",
        "third_party/include",
    ],
    deps = [
        ":AdvancedLib",
    ],
    defines = [
        "VERSION=\\\"1.0.0\\\"",
        "ENABLE_TESTS",
    ],
)

# Generated header
genrule(
    name = "generate_headers",
    srcs = ["config.json"],
    outs = ["generated.h"],
    cmd = "echo '#define GENERATED 1' > $(OUTS)",
)