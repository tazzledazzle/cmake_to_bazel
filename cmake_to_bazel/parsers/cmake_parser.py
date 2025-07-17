# cmake_to_bazel/parsers/cmake_parser.py

import os
import re
from typing import Dict, List, Optional, Any, Tuple


class CMakeParser:
    """
    A parser for CMake files that extracts build targets and configurations.
    
    This class is responsible for parsing CMakeLists.txt files and extracting
    relevant information such as targets, dependencies, and include directories.
    """
    
    def __init__(self):
        """Initialize the CMake parser."""
        # Regular expressions for parsing common CMake commands
        self.re_project = re.compile(r'project\s*\(\s*([^\s\)]+)')
        
        # Enhanced regex for add_executable to handle various formats
        # Format 1: add_executable(target source1 source2 ...)
        # Format 2: add_executable(target SOURCES source1 source2 ...)
        # Format 3: add_executable(target WIN32|MACOSX_BUNDLE|EXCLUDE_FROM_ALL source1 source2 ...)
        self.re_add_executable = re.compile(
            r'add_executable\s*\(\s*([^\s\)]+)\s+' # Target name
            r'(?:(WIN32|MACOSX_BUNDLE|EXCLUDE_FROM_ALL)\s+)?' # Optional keywords
            r'(?:SOURCES\s+)?' # Optional SOURCES keyword
            r'(.*?)\)', # Source files
            re.DOTALL
        )
        
        # Enhanced regex for add_library to handle various formats
        # Format 1: add_library(target [STATIC|SHARED|MODULE|INTERFACE|OBJECT] source1 source2 ...)
        # Format 2: add_library(target [STATIC|SHARED|MODULE|INTERFACE|OBJECT] SOURCES source1 source2 ...)
        # Format 3: add_library(target [STATIC|SHARED|MODULE|INTERFACE|OBJECT] IMPORTED|ALIAS|INTERFACE)
        # Format 4: add_library(target INTERFACE) - Interface library with no sources
        self.re_add_library = re.compile(
            r'add_library\s*\(\s*([^\s\)]+)\s+' # Target name
            r'(?:(STATIC|SHARED|MODULE|INTERFACE|OBJECT)\s+)?' # Optional library type
            r'(?:(IMPORTED|ALIAS|INTERFACE)\s*)?' # Optional library specifier
            r'(?:SOURCES\s+)?' # Optional SOURCES keyword
            r'(.*?)\)', # Source files (may be empty for IMPORTED/ALIAS/INTERFACE)
            re.DOTALL
        )
        
        # Enhanced regex for include_directories to handle various formats
        # Format 1: include_directories(dir1 dir2 ...)
        # Format 2: include_directories(AFTER|BEFORE|SYSTEM dir1 dir2 ...)
        self.re_include_directories = re.compile(
            r'include_directories\s*\(\s*'  # Command name and opening parenthesis
            r'(?:(AFTER|BEFORE|SYSTEM)\s+)?' # Optional keywords
            r'(.*?)\)', # Directories
            re.DOTALL
        )
        
        # Enhanced regex for target_include_directories to handle various formats
        # Format 1: target_include_directories(target [SYSTEM] [BEFORE|AFTER] <INTERFACE|PUBLIC|PRIVATE> dir1 dir2 ...)
        self.re_target_include_directories = re.compile(
            r'target_include_directories\s*\(\s*'  # Command name and opening parenthesis
            r'([^\s\)]+)\s+'  # Target name
            r'(?:(SYSTEM)\s+)?'  # Optional SYSTEM keyword
            r'(?:(BEFORE|AFTER)\s+)?'  # Optional BEFORE/AFTER keyword
            r'(INTERFACE|PUBLIC|PRIVATE)\s+'  # Scope keyword
            r'(.*?)\)', # Directories
            re.DOTALL
        )
        
        self.re_cmake_minimum_required = re.compile(r'cmake_minimum_required\s*\(\s*VERSION\s+([^\s\)]+)')
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a CMakeLists.txt file.
        
        Args:
            file_path: Path to the CMakeLists.txt file
            
        Returns:
            Dictionary representing the parsed content
        
        Raises:
            FileNotFoundError: If the file does not exist
            IOError: If there's an error reading the file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CMake file not found: {file_path}")
        
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return self.parse_string(content)
        except IOError as e:
            raise IOError(f"Error reading CMake file: {e}")
    
    def parse_string(self, content: str) -> Dict[str, Any]:
        """
        Parse CMake content from a string.
        
        Args:
            content: CMake content as string
            
        Returns:
            Dictionary representing the parsed content
        """
        # Initialize the result dictionary
        result = {
            'project': None,
            'minimum_required_version': None,
            'include_directories': [],
            'targets': [],
        }
        
        # Debug: Print the content for debugging
        # print(f"Parsing content: {content}")
        
        # Extract project name
        project_match = self.re_project.search(content)
        if project_match:
            result['project'] = project_match.group(1)
        
        # Extract minimum required CMake version
        version_match = self.re_cmake_minimum_required.search(content)
        if version_match:
            result['minimum_required_version'] = version_match.group(1)
        
        # Extract include directories - handle multi-line include_directories
        # First, normalize the content by removing newlines within parentheses
        normalized_content = self._normalize_multiline_commands(content)
        include_dirs_matches = self.re_include_directories.finditer(normalized_content)
        for match in include_dirs_matches:
            # Check if there's an optional keyword (AFTER, BEFORE, SYSTEM)
            keyword = match.group(1)
            # Get the directories from the second capture group
            dirs_str = match.group(2) if match.group(2) else ''
            dirs = self._parse_arguments(dirs_str)
            
            # Store the keyword as metadata if present
            if keyword:
                for dir_path in dirs:
                    # Add the directory with its keyword as metadata
                    if 'include_directories_metadata' not in result:
                        result['include_directories_metadata'] = {}
                    result['include_directories_metadata'][dir_path] = keyword
            
            # Add all directories to the main list
            result['include_directories'].extend(dirs)
        
        # Extract executable targets
        executable_matches = self.re_add_executable.finditer(content)
        for match in executable_matches:
            target_name = match.group(1)
            target_options = match.group(2) if match.group(2) else None
            sources_str = match.group(3) if match.group(3) else ''
            
            # Parse source files
            sources = self._parse_arguments(sources_str)
            
            # Create target entry
            target_entry = {
                'type': 'executable',
                'name': target_name,
                'sources': sources,
                'dependencies': []
            }
            
            # Add options if present
            if target_options:
                target_entry['options'] = target_options
                
            result['targets'].append(target_entry)
        
        # Extract library targets
        library_matches = self.re_add_library.finditer(content)
        for match in library_matches:
            target_name = match.group(1)
            lib_type = match.group(2) if match.group(2) else 'STATIC'  # Default to STATIC if not specified
            lib_specifier = match.group(3) if match.group(3) else None
            sources_str = match.group(4) if match.group(4) else ''
            
            # Parse source files
            sources = self._parse_arguments(sources_str)
            
            # Create target entry
            target_entry = {
                'type': 'library',
                'name': target_name,
                'library_type': lib_type,
                'sources': sources,
                'dependencies': []
            }
            
            # Handle special cases for library types and specifiers
            if lib_type == 'INTERFACE':
                # INTERFACE libraries don't have sources
                target_entry['sources'] = []
            
            # Add library specifier if present
            if lib_specifier:
                target_entry['library_specifier'] = lib_specifier
                
                # Special case for INTERFACE libraries
                if lib_specifier == 'INTERFACE':
                    target_entry['library_type'] = 'INTERFACE'
                    target_entry['sources'] = []
                
                # For IMPORTED libraries, sources should be empty
                if lib_specifier == 'IMPORTED':
                    target_entry['sources'] = []
                
            result['targets'].append(target_entry)
        
        # Extract target-specific include directories (after targets are parsed)
        target_include_dirs_matches = self.re_target_include_directories.finditer(normalized_content)
        for match in target_include_dirs_matches:
            target_name = match.group(1)
            system_flag = match.group(2)  # SYSTEM flag (optional)
            position_flag = match.group(3)  # BEFORE/AFTER flag (optional)
            scope = match.group(4)  # INTERFACE, PUBLIC, or PRIVATE
            dirs_str = match.group(5) if match.group(5) else ''
            dirs = self._parse_arguments(dirs_str)
            
            # Find the target in the targets list
            target_entry = None
            for t in result['targets']:
                if t['name'] == target_name:
                    target_entry = t
                    break
            
            # If target not found, skip this target_include_directories command
            if not target_entry:
                continue
                
            # Initialize include_directories for the target if not present
            if 'include_directories' not in target_entry:
                target_entry['include_directories'] = {
                    'INTERFACE': [],
                    'PUBLIC': [],
                    'PRIVATE': []
                }
                
            # Add directories to the appropriate scope
            target_entry['include_directories'][scope].extend(dirs)
            
            # Store metadata if present
            if system_flag or position_flag:
                if 'include_directories_metadata' not in target_entry:
                    target_entry['include_directories_metadata'] = {}
                    
                for dir_path in dirs:
                    metadata = {}
                    if system_flag:
                        metadata['system'] = True
                    if position_flag:
                        metadata['position'] = position_flag
                    target_entry['include_directories_metadata'][dir_path] = metadata
        
        return result
    
    def _normalize_multiline_commands(self, content: str) -> str:
        """
        Normalize multi-line CMake commands by removing newlines within parentheses.
        
        Args:
            content: CMake content as string
            
        Returns:
            Normalized content with newlines removed within parentheses
        """
        result = []
        paren_level = 0
        for char in content:
            if char == '(':
                paren_level += 1
                result.append(char)
            elif char == ')':
                paren_level -= 1
                result.append(char)
            elif char in ['\n', '\r'] and paren_level > 0:
                # Replace newlines within parentheses with spaces
                result.append(' ')
            else:
                result.append(char)
        return ''.join(result)
    
    def _parse_arguments(self, args_str: str) -> List[str]:
        """
        Parse arguments from a CMake command.
        
        Args:
            args_str: String containing arguments
            
        Returns:
            List of parsed arguments
        """
        # Handle quoted arguments and comments
        args = []
        current_arg = ''
        in_quotes = False
        i = 0
        
        while i < len(args_str):
            char = args_str[i]
            
            # Handle comments - skip everything after # until end of line or end of string
            if char == '#' and not in_quotes:
                # Add current argument if we have one
                if current_arg:
                    args.append(current_arg)
                    current_arg = ''
                
                # Skip to the end of the line or end of string
                while i < len(args_str) and args_str[i] not in ['\n', '\r']:
                    i += 1
                
                # Skip the newline character if present
                if i < len(args_str) and args_str[i] in ['\n', '\r']:
                    i += 1
                continue
            
            # Handle quotes
            if char == '"' and (not current_arg or current_arg[-1] != '\\'):
                in_quotes = not in_quotes
                current_arg += char
            elif char.isspace() and not in_quotes:
                if current_arg:
                    args.append(current_arg)
                    current_arg = ''
            else:
                current_arg += char
            
            i += 1
        
        if current_arg:
            args.append(current_arg)
        
        # Clean up arguments (remove quotes, extra whitespace)
        cleaned_args = []
        for arg in args:
            arg = arg.strip()
            if arg:
                # Remove surrounding quotes if present
                if (arg.startswith('"') and arg.endswith('"')) or \
                   (arg.startswith("'") and arg.endswith("'")):
                    arg = arg[1:-1]
                cleaned_args.append(arg)
        
        return cleaned_args


def parse_cmake(file_path: str) -> Dict[str, Any]:
    """
    Legacy function for backward compatibility.
    
    Args:
        file_path: Path to CMakeLists.txt file
        
    Returns:
        Dictionary with parsed content
    """
    parser = CMakeParser()
    return parser.parse_file(file_path)