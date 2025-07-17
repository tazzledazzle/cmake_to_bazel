#!/usr/bin/env python3

from cmake_to_bazel.parsers.cmake_parser import CMakeParser

parser = CMakeParser()

content = """
include_directories(
    ${PROJECT_SOURCE_DIR}/include # Main include directory
    /usr/local/include # System includes
)
"""

result = parser.parse_string(content)
print("Result:", result)
print("Include directories:", result["include_directories"])
print("Length:", len(result["include_directories"]))