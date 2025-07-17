# CMake to Bazel Transpiler User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Command Line Interface](#command-line-interface)
4. [Configuration](#configuration)
5. [Supported CMake Features](#supported-cmake-features)
6. [Generated Bazel Rules](#generated-bazel-rules)
7. [Advanced Usage](#advanced-usage)
8. [Troubleshooting](#troubleshooting)

## Introduction

The CMake to Bazel Transpiler is a tool designed to automate the conversion of CMake build configurations to Bazel build configurations. It parses CMakeLists.txt files, extracts build targets, dependencies, and other configuration details, and generates equivalent Bazel BUILD files.

### Key Benefits

- **Automated Migration**: Reduce the manual effort required to migrate from CMake to Bazel
- **Consistency**: Ensure consistent conversion of build configurations
- **Customization**: Adapt the conversion process to project-specific requirements
- **Error Reporting**: Receive clear error messages and suggestions for unsupported features

## Installation

### Prerequisites

- Python 3.6 or higher
- Bazel 6.0 or higher (if using Bazel rules)

### Installation Methods

#### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/tazzledazzle/cmake-to-bazel.git
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

#### Using pip (coming soon)

```bash
pip install cmake-to-bazel
```

## Command Line Interface

### Basic Usage

```bash
python -m cmake_to_bazel.main /path/to/CMakeLists.txt /output/directory
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `CMAKE_FILE` | Path to the CMakeLists.txt file (required) |
| `OUTPUT_DIR` | Directory where Bazel BUILD files will be generated (required) |
| `--config FILE` | Path to configuration file |
| `--verbose` | Enable verbose output |
| `--dry-run` | Show what would be generated without writing files |
| `--help` | Show help message and exit |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CMAKE_TO_BAZEL_CONFIG` | Path to default configuration file | None |
| `CMAKE_TO_BAZEL_VERBOSE` | Enable verbose output | False |

## Configuration

The transpiler can be customized using a JSON configuration file. This file allows you to specify custom mappings, additional dependencies, and excluded targets.

### Configuration File Format

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

### Configuration Options

#### Mappings

The `mappings` section allows you to define custom mappings from CMake functions to Bazel rules. Each mapping includes:

- `rule`: The Bazel rule to generate
- `attributes`: A mapping from CMake attributes to Bazel attributes

Example:
```json
"add_custom_target": {
  "rule": "genrule",
  "attributes": {
    "COMMAND": "cmd",
    "DEPENDS": "tools",
    "OUTPUT": "outs"
  }
}
```

#### Additional Dependencies

The `additional_dependencies` section allows you to specify additional dependencies for targets that may not be explicitly stated in the CMake files.

Example:
```json
"MyExecutable": [
  "@boost//:filesystem",
  "@openssl//:ssl"
]
```

#### Excluded Targets

The `excluded_targets` section allows you to specify targets that should be excluded from the transpilation process.

Example:
```json
[
  "test_target",
  "benchmark_target"
]
```

## Supported CMake Features

The transpiler supports the following CMake features:

### Project Definition

- `cmake_minimum_required`
- `project`

### Targets

- `add_executable`
- `add_library`
- `target_link_libraries`
- `target_include_directories`
- `target_compile_definitions`
- `target_compile_options`

### Directories

- `include_directories`
- `link_directories`

### Variables

- Variable definition and substitution
- List variables
- Path variables

### Control Flow

- `if`/`else`/`endif`
- `foreach`/`endforeach`

### Functions and Macros

- `function`/`endfunction`
- `macro`/`endmacro`

## Generated Bazel Rules

The transpiler generates the following Bazel rules:

### C/C++ Rules

- `cc_binary`: For executable targets
- `cc_library`: For library targets
- `cc_test`: For test targets

### File Generation Rules

- `genrule`: For custom commands

### Other Rules

- `filegroup`: For file collections
- `alias`: For target aliases

## Advanced Usage

### Using with Bazel Rules

You can use the transpiler as a Bazel rule in your BUILD files:

```python
load("@cmake_to_bazel//:cmake_to_bazel.bzl", "cmake_to_bazel")

cmake_to_bazel(
    name = "convert_cmake",
    cmake_file = "path/to/CMakeLists.txt",
    output_dir = "bazel_output",
)
```

### Incremental Conversion

For large projects, you may want to convert one directory at a time:

```bash
for dir in $(find . -name CMakeLists.txt -exec dirname {} \;); do
  python -m cmake_to_bazel.main $dir/CMakeLists.txt $dir
done
```

### Integration with CI/CD

You can integrate the transpiler into your CI/CD pipeline to automatically generate Bazel BUILD files from CMake files:

```yaml
# Example GitHub Actions workflow
name: Generate Bazel BUILD files

on:
  push:
    paths:
      - '**/*.cmake'
      - '**/CMakeLists.txt'

jobs:
  convert:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Convert CMake to Bazel
        run: python -m cmake_to_bazel.main /path/to/CMakeLists.txt /output/directory
      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add .
          git commit -m "Generate Bazel BUILD files" || echo "No changes to commit"
          git push
```

## Troubleshooting

See the [Troubleshooting Guide](troubleshooting.md) for common issues and solutions.