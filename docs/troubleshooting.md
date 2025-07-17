# Troubleshooting Guide

This guide addresses common issues that may arise when using the CMake to Bazel transpiler and provides solutions to resolve them.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Parsing Errors](#parsing-errors)
3. [Rule Generation Issues](#rule-generation-issues)
4. [Build Errors](#build-errors)
5. [Configuration Issues](#configuration-issues)
6. [Common CMake Features Not Supported](#common-cmake-features-not-supported)
7. [Performance Issues](#performance-issues)

## Installation Issues

### Python Version Compatibility

**Issue**: Error message indicating incompatible Python version.

**Solution**: Ensure you're using Python 3.6 or higher. Check your Python version with:

```bash
python --version
```

If you have multiple Python versions installed, you may need to use `python3` explicitly:

```bash
python3 -m cmake_to_bazel.main /path/to/CMakeLists.txt /output/directory
```

### Missing Dependencies

**Issue**: ImportError or ModuleNotFoundError when running the tool.

**Solution**: Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Bazel Version Compatibility

**Issue**: Error messages when using the generated BUILD files with Bazel.

**Solution**: Ensure you're using Bazel 6.0 or higher. Check your Bazel version with:

```bash
bazel --version
```

## Parsing Errors

### Syntax Errors in CMakeLists.txt

**Issue**: Error message indicating a syntax error in the CMakeLists.txt file.

**Solution**: 
1. Check the error message for the line number and context.
2. Verify the syntax in the CMakeLists.txt file.
3. Fix any syntax errors in the CMakeLists.txt file.

### Unsupported CMake Commands

**Issue**: Error or warning about unsupported CMake commands.

**Solution**:
1. Check if there's a suggested workaround in the error message.
2. Add a custom mapping in the configuration file for the unsupported command.
3. Modify the CMakeLists.txt file to use supported commands if possible.

### Variable Resolution Failures

**Issue**: Error about unresolved variables in the CMakeLists.txt file.

**Solution**:
1. Ensure all variables are properly defined before use.
2. Check for typos in variable names.
3. For environment variables, ensure they are properly set.

## Rule Generation Issues

### Missing Dependencies

**Issue**: Generated BUILD files have missing dependencies.

**Solution**:
1. Use the configuration file to specify additional dependencies:
   ```json
   {
     "additional_dependencies": {
       "target_name": [
         "additional_dep1",
         "additional_dep2"
       ]
     }
   }
   ```
2. Ensure all dependencies are properly specified in the CMakeLists.txt file.

### Incorrect Rule Type

**Issue**: Generated rules have incorrect types (e.g., library instead of binary).

**Solution**:
1. Check the CMakeLists.txt file for correct target definitions.
2. Use the configuration file to override rule types if necessary.

### Source File Path Issues

**Issue**: Generated rules have incorrect source file paths.

**Solution**:
1. Ensure source file paths in the CMakeLists.txt file are relative to the project root.
2. Check for variable substitutions in file paths.

## Build Errors

### Compilation Errors

**Issue**: Generated BUILD files produce compilation errors when built with Bazel.

**Solution**:
1. Check the error messages for specific issues.
2. Ensure all include directories are properly specified.
3. Verify that compile definitions and options are correctly translated.
4. Manually adjust the generated BUILD files if necessary.

### Linking Errors

**Issue**: Generated BUILD files produce linking errors when built with Bazel.

**Solution**:
1. Check for missing dependencies in the generated BUILD files.
2. Ensure all libraries are properly linked.
3. Add any missing system libraries using `linkopts`.

### Header File Not Found

**Issue**: Bazel build fails with "header file not found" errors.

**Solution**:
1. Ensure all include directories are properly specified in the generated BUILD files.
2. Check that header files are properly exported in library targets.
3. Use `hdrs` attribute for header files that need to be exported.

## Configuration Issues

### Configuration File Syntax

**Issue**: Error parsing the configuration file.

**Solution**:
1. Ensure the configuration file is valid JSON.
2. Check for missing commas, brackets, or quotes.
3. Use a JSON validator to verify the syntax.

### Configuration Options Not Applied

**Issue**: Configuration options are not being applied to the generated BUILD files.

**Solution**:
1. Ensure the configuration file is being properly loaded.
2. Check for typos in target names or option names.
3. Verify the configuration file format matches the expected format.

## Common CMake Features Not Supported

### Custom Commands

**Issue**: Custom commands in CMakeLists.txt are not properly translated.

**Solution**:
1. Use the configuration file to map custom commands to Bazel rules.
2. For complex custom commands, consider using `genrule` or custom Bazel rules.

### Generator Expressions

**Issue**: CMake generator expressions are not properly evaluated.

**Solution**:
1. Replace generator expressions with explicit values if possible.
2. Use the configuration file to specify how generator expressions should be translated.

### Find Modules

**Issue**: CMake find_package commands are not properly translated.

**Solution**:
1. Add external dependencies directly in the WORKSPACE file.
2. Use the configuration file to map find_package calls to Bazel dependencies.

## Performance Issues

### Slow Parsing

**Issue**: Parsing large CMakeLists.txt files is slow.

**Solution**:
1. Split large CMakeLists.txt files into smaller files.
2. Use the `--verbose` option to identify bottlenecks.
3. Consider using incremental conversion for large projects.

### Memory Usage

**Issue**: High memory usage when parsing large projects.

**Solution**:
1. Process one directory at a time.
2. Increase available memory if possible.
3. Use the `--dry-run` option to test without generating files.

## Getting Help

If you encounter issues not covered in this guide, please:

1. Check the [GitHub issues](https://github.com/yourusername/cmake-to-bazel-transpiler/issues) for similar problems and solutions.
2. Create a new issue with:
   - A detailed description of the problem
   - Steps to reproduce the issue
   - Relevant parts of the CMakeLists.txt file
   - Error messages or unexpected behavior
3. For urgent issues, contact the maintainers directly.