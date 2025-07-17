#!/usr/bin/env python3

from cmake_to_bazel.parsers.cmake_parser import CMakeParser

def test_comment_parsing():
    parser = CMakeParser()
    
    content = """
    include_directories(
        ${PROJECT_SOURCE_DIR}/include # Main include directory
        /usr/local/include # System includes
    )
    """
    
    print("Original content:")
    print(repr(content))
    
    processed_content = parser._process_conditional_statements(content)
    print("\nProcessed content:")
    print(repr(processed_content))
    
    normalized_content = parser._normalize_multiline_commands(processed_content)
    print("\nNormalized content:")
    print(repr(normalized_content))
    
    result = parser.parse_string(content)
    print("\nParsed result:")
    print(f"Include directories: {result['include_directories']}")
    print(f"Count: {len(result['include_directories'])}")

if __name__ == "__main__":
    test_comment_parsing()