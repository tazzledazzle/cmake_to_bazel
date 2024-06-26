# CMake to Bazel Transpiler

This tool generates Bazel `BUILD` files from `CMakeLists.txt` files using custom Bazel rules.

## Features

- Parses `CMakeLists.txt` files.
- Generates Bazel `BUILD` files.
- Supports custom Bazel rules for flexibility.

## Requirements

- Java 8 or higher


## Installation

Clone the repository and build the project using:

```shell
git clone https://github.com/tazzledazzle/cmake_to_bazel
bazel run //cmake_to_bazel:generate_bazel_build

```