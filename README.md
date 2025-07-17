# CMake to Bazel Transpiler

A Python-based tool that automatically converts CMake build configurations to Bazel build configurations. This tool simplifies the migration process from CMake to Bazel by generating equivalent Bazel BUILD files from CMakeLists.txt files.

## Features

- Parses CMakeLists.txt files and extracts build targets, dependencies, and configurations
- Generates valid Bazel BUILD files with equivalent build rules
- Supports common CMake constructs:
  - Executable targets (add_executable)
  - Library targets (add_library)
  - Include directories (include_directories)
  - Target dependencies (target_link_libraries)
  - Variable resolution
  - Conditional statements
- Provides customization options through configuration files
- Includes comprehensive error reporting and suggestions

## Requirements

- Python 3.6 or higher
- Bazel 6.0 or higher

## Installation

### Option 1: Install from source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cmake-to-bazel-transpiler.git
   cd cmake-to-bazel-transpiler
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Build with Bazel:
   ```bash
   bazel build //cmake_to_bazel:main
   ```

### Option 2: Install with pip (coming soon)

```bash
pip install cmake-to-bazel
```

## Usage

### Basic Usage

Convert a single CMakeLists.txt file to a Bazel BUILD file:

```bash
python -m cmake_to_bazel.main /path/to/CMakeLists.txt /output/directory
```

Or use the Bazel rule:

```python
load("@cmake_to_bazel//:cmake_to_bazel.bzl", "cmake_to_bazel")

cmake_to_bazel(
    name = "convert_cmake",
    cmake_file = "path/to/CMakeLists.txt",
    output_dir = "bazel_output",
)
```

### Command Line Options

```
Usage: python -m cmake_to_bazel.main [OPTIONS] CMAKE_FILE OUTPUT_DIR

Arguments:
  CMAKE_FILE    Path to the CMakeLists.txt file
  OUTPUT_DIR    Directory where Bazel BUILD files will be generated

Options:
  --config FILE       Path to configuration file
  --verbose           Enable verbose output
  --dry-run           Show what would be generated without writing files
  --help              Show this help message and exit
```

### Configuration File

You can customize the transpilation process using a JSON configuration file:

```json
{
  "mappings": {
    "custom_cmake_function": {
      "rule": "custom_bazel_rule",
      "attributes": {
        "cmake_attr": "bazel_attr"
      }
    }
  },
  "additional_dependencies": {
    "target_name": [
      "additional_dep1",
      "additional_dep2"
    ]
  },
  "excluded_targets": [
    "target_to_exclude"
  ]
}
```

## Examples

### Simple Example

**CMakeLists.txt**:
```cmake
cmake_minimum_required(VERSION 3.10)
project(SimpleProject)

# Include directories
include_directories(${PROJECT_SOURCE_DIR}/include)

# Add an executable target
add_executable(MyApp src/main.cpp src/helper.cpp)

# Add a library target
add_library(MyLib src/lib.cpp)

# Link the library to the executable
target_link_libraries(MyApp MyLib)
```

**Generated BUILD file**:
```python
cc_library(
    name = "MyLib",
    srcs = ["src/lib.cpp"],
    includes = ["include"],
)

cc_binary(
    name = "MyApp",
    srcs = [
        "src/main.cpp",
        "src/helper.cpp",
    ],
    includes = ["include"],
    deps = [":MyLib"],
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.