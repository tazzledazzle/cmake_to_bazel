#!/usr/bin/env python3

from cmake_to_bazel.parsers.cmake_parser import CMakeParser

def debug_parsing():
    parser = CMakeParser()
    
    # Test case 1: Comments
    print("=== Testing comments ===")
    content1 = """
        add_executable(MyApp src/main.cpp)
        target_link_libraries(MyApp
            MyLib1  # Main library
            MyLib2  # Utility library
        )
        """
    
    # Let's see what the normalized content looks like
    normalized = parser._normalize_multiline_commands(content1)
    print(f"Normalized content: {repr(normalized)}")
    
    # Let's see what the regex matches
    import re
    matches = parser.re_target_link_libraries.finditer(normalized)
    for match in matches:
        print(f"Match groups: {match.groups()}")
        deps_str = match.group(2) if match.group(2) else ''
        print(f"Dependencies string: {repr(deps_str)}")
        parsed_deps = parser._parse_arguments(deps_str)
        print(f"Parsed dependencies: {parsed_deps}")
    
    result1 = parser.parse_string(content1)
    target1 = result1["targets"][0]
    print(f"Dependencies: {target1['dependencies']}")
    print(f"PRIVATE deps: {target1['dependencies']['PRIVATE']}")
    print()
    
    # Test case 2: Quoted names
    print("=== Testing quoted names ===")
    content2 = """
        add_executable(MyApp src/main.cpp)
        target_link_libraries(MyApp "lib with spaces" 'another lib')
        """
    result2 = parser.parse_string(content2)
    target2 = result2["targets"][0]
    print(f"Dependencies: {target2['dependencies']}")
    print(f"PRIVATE deps: {target2['dependencies']['PRIVATE']}")

if __name__ == "__main__":
    debug_parsing()