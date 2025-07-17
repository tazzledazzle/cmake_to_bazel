# Debug script for CMake parser

from cmake_to_bazel.parsers.cmake_parser import CMakeParser

def debug_include_directories_with_comments():
    parser = CMakeParser()
    content = """
    include_directories(
        ${PROJECT_SOURCE_DIR}/include # Main include directory
        /usr/local/include # System includes
    )
    """
    
    print("Original content:")
    print(content)
    
    # Normalize content
    normalized_content = parser._normalize_multiline_commands(content)
    print("\nNormalized content:")
    print(normalized_content)
    
    # Extract include directories
    include_dirs_matches = parser.re_include_directories.finditer(normalized_content)
    for match in include_dirs_matches:
        print("\nMatch found:")
        print(f"Group 1 (keyword): {match.group(1)}")
        print(f"Group 2 (dirs): {match.group(2)}")
        
        # Parse arguments
        dirs_str = match.group(2) if match.group(2) else ''
        print(f"\nParsing arguments from: '{dirs_str}'")
        
        # Debug the argument parsing
        args = []
        current_arg = ''
        in_quotes = False
        i = 0
        
        print("\nParsing process:")
        while i < len(dirs_str):
            char = dirs_str[i]
            print(f"Position {i}, Char: '{char}', Current arg: '{current_arg}', In quotes: {in_quotes}")
            
            # Handle comments - skip everything after # until end of line
            if char == '#' and not in_quotes:
                print(f"  Found comment at position {i}")
                # Skip to the end of the line
                start_i = i
                while i < len(dirs_str) and dirs_str[i] not in ['\n', '\r']:
                    i += 1
                print(f"  Skipped comment from position {start_i} to {i}")
                if i < len(dirs_str):
                    i += 1  # Skip the newline character
                    print(f"  Skipped newline, now at position {i}")
                continue
            
            # Handle quotes
            if char == '"' and (not current_arg or current_arg[-1] != '\\'):
                in_quotes = not in_quotes
                current_arg += char
                print(f"  Toggle quotes: {in_quotes}")
            elif char.isspace() and not in_quotes:
                if current_arg:
                    args.append(current_arg)
                    print(f"  Added argument: '{current_arg}'")
                    current_arg = ''
            else:
                current_arg += char
            
            i += 1
        
        if current_arg:
            args.append(current_arg)
            print(f"  Added final argument: '{current_arg}'")
        
        print("\nRaw arguments:")
        for arg in args:
            print(f"  '{arg}'")
        
        # Clean up arguments
        cleaned_args = []
        for arg in args:
            arg = arg.strip()
            if arg:
                # Remove surrounding quotes if present
                if (arg.startswith('"') and arg.endswith('"')) or \
                   (arg.startswith("'") and arg.endswith("'")):
                    arg = arg[1:-1]
                cleaned_args.append(arg)
        
        print("\nCleaned arguments:")
        for arg in cleaned_args:
            print(f"  '{arg}'")

if __name__ == "__main__":
    debug_include_directories_with_comments()