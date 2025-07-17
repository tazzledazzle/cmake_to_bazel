# Common CMake Patterns and Their Bazel Equivalents

This guide documents common CMake patterns and how they are translated to Bazel by the CMake to Bazel transpiler.

## Table of Contents

1. [Basic Project Structure](#basic-project-structure)
2. [Executable and Library Targets](#executable-and-library-targets)
3. [Include Directories](#include-directories)
4. [Dependencies](#dependencies)
5. [Compile Definitions and Options](#compile-definitions-and-options)
6. [Variables and Lists](#variables-and-lists)
7. [Conditional Compilation](#conditional-compilation)
8. [Custom Commands and Targets](#custom-commands-and-targets)
9. [Testing](#testing)
10. [External Dependencies](#external-dependencies)

## Basic Project Structure

### CMake

```cmake
cmake_minimum_required(VERSION 3.10)
project(MyProject)
```

### Bazel

In Bazel, project structure is defined by the presence of BUILD files in directories. There's no direct equivalent to `cmake_minimum_required` or `project` in Bazel.

## Executable and Library Targets

### CMake

```cmake
# Executable
add_executable(MyApp src/main.cpp src/helper.cpp)

# Static library
add_library(MyLib STATIC src/lib.cpp)

# Shared library
add_library(MySharedLib SHARED src/shared_lib.cpp)

# Object library
add_library(MyObjLib OBJECT src/obj_lib.cpp)
```

### Bazel

```python
# Executable
cc_binary(
    name = "MyApp",
    srcs = [
        "src/main.cpp",
        "src/helper.cpp",
    ],
)

# Static library
cc_library(
    name = "MyLib",
    srcs = ["src/lib.cpp"],
)

# Shared library
cc_library(
    name = "MySharedLib",
    srcs = ["src/shared_lib.cpp"],
    linkstatic = False,
)

# Object library (no direct equivalent, use filegroup)
filegroup(
    name = "MyObjLib",
    srcs = ["src/obj_lib.cpp"],
)
```

## Include Directories

### CMake

```cmake
# Global include directories
include_directories(
    ${PROJECT_SOURCE_DIR}/include
    ${PROJECT_SOURCE_DIR}/third_party/include
)

# Target-specific include directories
target_include_directories(MyLib PUBLIC
    ${PROJECT_SOURCE_DIR}/public_include
)
target_include_directories(MyLib PRIVATE
    ${PROJECT_SOURCE_DIR}/private_include
)
```

### Bazel

```python
# Global include directories are applied to all targets
cc_library(
    name = "MyLib",
    srcs = ["src/lib.cpp"],
    includes = [
        "include",
        "third_party/include",
        "public_include",  # PUBLIC includes
    ],
    copts = [
        "-Iprivate_include",  # PRIVATE includes
    ],
)
```

## Dependencies

### CMake

```cmake
# Link libraries
target_link_libraries(MyApp
    MyLib
    pthread
    dl
)

# Link libraries with visibility
target_link_libraries(MyApp PUBLIC MyLib)
target_link_libraries(MyApp PRIVATE SecretLib)
```

### Bazel

```python
cc_binary(
    name = "MyApp",
    srcs = ["src/main.cpp"],
    deps = [
        ":MyLib",  # Direct dependency
        ":SecretLib",  # PRIVATE dependency
    ],
    linkopts = [
        "-lpthread",
        "-ldl",
    ],
)

# PUBLIC dependencies are propagated
cc_library(
    name = "MyLib",
    srcs = ["src/lib.cpp"],
    deps = [":PublicDep"],  # This will be visible to targets depending on MyLib
)
```

## Compile Definitions and Options

### CMake

```cmake
# Global compile definitions
add_compile_definitions(VERSION="1.0.0" DEBUG)

# Target-specific compile definitions
target_compile_definitions(MyLib PRIVATE INTERNAL_BUILD)
target_compile_definitions(MyLib PUBLIC API_VERSION=2)

# Compile options
add_compile_options(-Wall -Werror)
target_compile_options(MyLib PRIVATE -fvisibility=hidden)
```

### Bazel

```python
cc_library(
    name = "MyLib",
    srcs = ["src/lib.cpp"],
    defines = [
        "VERSION=\\\"1.0.0\\\"",
        "DEBUG",
        "INTERNAL_BUILD",  # PRIVATE define
        "API_VERSION=2",   # PUBLIC define
    ],
    copts = [
        "-Wall",
        "-Werror",
        "-fvisibility=hidden",  # PRIVATE option
    ],
)
```

## Variables and Lists

### CMake

```cmake
# Simple variable
set(VERSION "1.0.0")

# List variable
set(SOURCES
    src/main.cpp
    src/helper.cpp
    src/utils.cpp
)

# Using variables
add_executable(MyApp ${SOURCES})
add_compile_definitions(VERSION=${VERSION})
```

### Bazel

```python
# Variables in Bazel are just Python variables
VERSION = "1.0.0"

SOURCES = [
    "src/main.cpp",
    "src/helper.cpp",
    "src/utils.cpp",
]

cc_binary(
    name = "MyApp",
    srcs = SOURCES,
    defines = ["VERSION=\\\"" + VERSION + "\\\""],
)
```

## Conditional Compilation

### CMake

```cmake
# Simple condition
if(ENABLE_FEATURE)
    add_compile_definitions(FEATURE_ENABLED)
endif()

# Complex condition
if(UNIX AND NOT APPLE)
    add_compile_definitions(LINUX_BUILD)
elseif(APPLE)
    add_compile_definitions(MACOS_BUILD)
else()
    add_compile_definitions(WINDOWS_BUILD)
endif()

# Feature toggle
option(ENABLE_TESTS "Enable tests" ON)
if(ENABLE_TESTS)
    add_executable(MyTests tests/test_main.cpp)
endif()
```

### Bazel

```python
# Bazel uses select() for conditional compilation
cc_binary(
    name = "MyApp",
    srcs = ["src/main.cpp"],
    defines = select({
        "//conditions:default": ["FEATURE_ENABLED"],
    }),
)

# Platform-specific defines
cc_binary(
    name = "MyApp",
    srcs = ["src/main.cpp"],
    defines = select({
        "@platforms//os:linux": ["LINUX_BUILD"],
        "@platforms//os:macos": ["MACOS_BUILD"],
        "@platforms//os:windows": ["WINDOWS_BUILD"],
        "//conditions:default": [],
    }),
)

# Feature toggle (using build flags)
# Use --define=enable_tests=true when building
cc_binary(
    name = "MyApp",
    srcs = ["src/main.cpp"],
    defines = select({
        ":enable_tests": ["ENABLE_TESTS"],
        "//conditions:default": [],
    }),
)

# Conditional target
# In Bazel, you would typically always define the target but control its building
cc_test(
    name = "MyTests",
    srcs = ["tests/test_main.cpp"],
    tags = ["manual"],  # Won't be built by default
)
```

## Custom Commands and Targets

### CMake

```cmake
# Custom command
add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/generated.h
    COMMAND ${CMAKE_COMMAND} -E echo "#define GENERATED 1" > ${CMAKE_CURRENT_BINARY_DIR}/generated.h
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/config.json
)

# Custom target
add_custom_target(
    generate_headers
    DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/generated.h
)
```

### Bazel

```python
# Custom command and target using genrule
genrule(
    name = "generate_headers",
    srcs = ["config.json"],
    outs = ["generated.h"],
    cmd = "echo '#define GENERATED 1' > $(OUTS)",
)
```

## Testing

### CMake

```cmake
# Enable testing
enable_testing()

# Add test
add_executable(MyTests tests/test_main.cpp)
target_link_libraries(MyTests MyLib)
add_test(NAME MyTests COMMAND MyTests)

# Test with arguments
add_test(NAME MyTestsWithArgs COMMAND MyTests --verbose)
```

### Bazel

```python
# Test target
cc_test(
    name = "MyTests",
    srcs = ["tests/test_main.cpp"],
    deps = [":MyLib"],
)

# Test with arguments
cc_test(
    name = "MyTestsWithArgs",
    srcs = ["tests/test_main.cpp"],
    deps = [":MyLib"],
    args = ["--verbose"],
)
```

## External Dependencies

### CMake

```cmake
# Find package
find_package(Boost REQUIRED COMPONENTS filesystem system)
include_directories(${Boost_INCLUDE_DIRS})
target_link_libraries(MyApp ${Boost_LIBRARIES})

# External project
include(ExternalProject)
ExternalProject_Add(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG main
    PREFIX ${CMAKE_CURRENT_BINARY_DIR}/googletest
    INSTALL_COMMAND ""
)
```

### Bazel

```python
# External dependencies in Bazel are typically defined in the WORKSPACE file
# and then referenced in BUILD files

# In WORKSPACE:
http_archive(
    name = "com_github_boost",
    urls = ["https://github.com/boostorg/boost/archive/boost-1.75.0.tar.gz"],
    strip_prefix = "boost-boost-1.75.0",
)

# In BUILD:
cc_binary(
    name = "MyApp",
    srcs = ["src/main.cpp"],
    deps = [
        "@com_github_boost//:filesystem",
        "@com_github_boost//:system",
    ],
)

# For googletest:
http_archive(
    name = "com_google_googletest",
    urls = ["https://github.com/google/googletest/archive/release-1.10.0.zip"],
    strip_prefix = "googletest-release-1.10.0",
)

cc_test(
    name = "MyTests",
    srcs = ["tests/test_main.cpp"],
    deps = [
        ":MyLib",
        "@com_google_googletest//:gtest_main",
    ],
)
```

## Best Practices for Migration

1. **Start with a clean Bazel workspace**: Don't try to mix CMake and Bazel builds in the same directory structure initially.

2. **Migrate incrementally**: Start with leaf libraries and work your way up to executables.

3. **Use the transpiler as a starting point**: The generated BUILD files may need manual adjustments for complex projects.

4. **Keep both build systems working during migration**: This allows for easier verification that the Bazel build produces equivalent results.

5. **Update your CI pipeline**: Make sure your CI system can build with both CMake and Bazel during the transition period.

6. **Test thoroughly**: Ensure that the Bazel-built binaries behave identically to the CMake-built ones.

7. **Consider using Bazel's CMake rules**: For very complex CMake projects, consider using Bazel's rules_foreign_cc to invoke CMake from Bazel.