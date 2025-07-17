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
        # Dictionary to store CMake variables
        self.variables = {}
        
        # Regular expressions for parsing common CMake commands
        self.re_project = re.compile(r'project\s*\(\s*([^\s\)]+)')
        
        # Regular expressions for conditional statements
        self.re_if = re.compile(r'if\s*\(\s*(.*?)\s*\)', re.IGNORECASE)
        self.re_elseif = re.compile(r'elseif\s*\(\s*(.*?)\s*\)', re.IGNORECASE)
        self.re_else = re.compile(r'else\s*\(\s*\)', re.IGNORECASE)
        self.re_endif = re.compile(r'endif\s*\(\s*\)', re.IGNORECASE)
        
        # Regular expressions for variable operations
        self.re_set = re.compile(r'set\s*\(\s*([^\s\)]+)(?:\s+(.*?))?\)', re.DOTALL)
        self.re_variable_ref = re.compile(r'\$\{([^}]+)\}')
        
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
        
        # Enhanced regex for target_link_libraries to handle various formats
        # Format 1: target_link_libraries(target lib1 lib2 ...)
        # Format 2: target_link_libraries(target [INTERFACE|PUBLIC|PRIVATE] lib1 lib2 ...)
        # Format 3: target_link_libraries(target [INTERFACE|PUBLIC|PRIVATE] [INTERFACE|PUBLIC|PRIVATE] lib1 lib2 ...)
        self.re_target_link_libraries = re.compile(
            r'target_link_libraries\s*\(\s*'  # Command name and opening parenthesis
            r'([^\s\)]+)\s+'  # Target name
            r'(.*?)\)', # Dependencies and optional scope keywords
            re.DOTALL
        )
        
        # Regular expressions for custom commands and macros
        self.re_add_custom_command = re.compile(
            r'add_custom_command\s*\(\s*(.*?)\)', 
            re.DOTALL
        )
        
        self.re_add_custom_target = re.compile(
            r'add_custom_target\s*\(\s*([^\s\)]+)\s+(.*?)\)', 
            re.DOTALL
        )
        
        self.re_macro = re.compile(
            r'macro\s*\(\s*([^\s\)]+)(?:\s+(.*?))?\)', 
            re.DOTALL
        )
        
        self.re_endmacro = re.compile(
            r'endmacro\s*\(\s*\)', 
            re.IGNORECASE
        )
        
        self.re_function = re.compile(
            r'function\s*\(\s*([^\s\)]+)(?:\s+(.*?))?\)', 
            re.DOTALL
        )
        
        self.re_endfunction = re.compile(
            r'endfunction\s*\(\s*\)', 
            re.IGNORECASE
        )
        
        # Predefined mappings for common custom commands/macros
        self.custom_command_mappings = {
            'add_custom_command': self._handle_add_custom_command,
            'add_custom_target': self._handle_add_custom_target,
            'macro': self._handle_macro_definition,
            'function': self._handle_function_definition,
        }
        
        # Storage for custom macros and functions
        self.custom_macros = {}
        self.custom_functions = {}
        self.custom_commands = []
        self.custom_targets = []
    
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
        
        # Process conditional statements first to get the effective content
        processed_content = self._process_conditional_statements(content)
        
        # Initialize built-in variables
        self._initialize_builtin_variables()
        
        # Extract project name first (before variable resolution)
        project_match = self.re_project.search(processed_content)
        if project_match:
            result['project'] = project_match.group(1)
            # Set PROJECT_NAME variable
            self.variables['PROJECT_NAME'] = project_match.group(1)
        
        # Extract and process variable definitions
        self._extract_variables(processed_content)
        
        # Resolve variables in the content
        resolved_content = self._resolve_variables(processed_content)
        
        # Extract minimum required CMake version
        version_match = self.re_cmake_minimum_required.search(resolved_content)
        if version_match:
            result['minimum_required_version'] = version_match.group(1)
        
        # Extract include directories - handle multi-line include_directories
        # First, normalize the content by removing newlines within parentheses
        normalized_content = self._normalize_multiline_commands(resolved_content)
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
        executable_matches = self.re_add_executable.finditer(normalized_content)
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
        library_matches = self.re_add_library.finditer(normalized_content)
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
        
        # Extract target link libraries (after targets are parsed)
        target_link_libraries_matches = self.re_target_link_libraries.finditer(normalized_content)
        for match in target_link_libraries_matches:
            target_name = match.group(1)
            dependencies_str = match.group(2) if match.group(2) else ''
            
            # Find the target in the targets list
            target_entry = None
            for t in result['targets']:
                if t['name'] == target_name:
                    target_entry = t
                    break
            
            # If target not found, skip this target_link_libraries command
            if not target_entry:
                continue
            
            # Parse dependencies with scope handling
            dependencies = self._parse_target_link_libraries_dependencies(dependencies_str)
            
            # Initialize dependencies structure if not present
            if not isinstance(target_entry['dependencies'], dict):
                target_entry['dependencies'] = {
                    'INTERFACE': [],
                    'PUBLIC': [],
                    'PRIVATE': []
                }
            
            # Add dependencies to the appropriate scopes
            for scope, deps in dependencies.items():
                target_entry['dependencies'][scope].extend(deps)
        
        # Process custom commands and macros
        self._process_custom_commands_and_macros(normalized_content)
        
        # Add custom commands and macros to result
        result['custom_commands'] = self.custom_commands.copy()
        result['custom_targets'] = self.custom_targets.copy()
        result['custom_macros'] = self.custom_macros.copy()
        result['custom_functions'] = self.custom_functions.copy()
        
        # Add variables to result for debugging/inspection
        result['variables'] = self.variables.copy()
        
        return result
    
    def _initialize_builtin_variables(self):
        """Initialize built-in CMake variables with default values."""
        # Common built-in variables
        self.variables.update({
            'CMAKE_CURRENT_SOURCE_DIR': '.',
            'CMAKE_CURRENT_BINARY_DIR': '.',
            'CMAKE_SOURCE_DIR': '.',
            'CMAKE_BINARY_DIR': '.',
            'PROJECT_SOURCE_DIR': '.',
            'PROJECT_BINARY_DIR': '.',
            'CMAKE_SYSTEM_NAME': 'Linux',
            'CMAKE_SYSTEM_VERSION': '1.0',
            'CMAKE_SYSTEM_PROCESSOR': 'x86_64',
            'CMAKE_CXX_COMPILER_ID': 'GNU',
            'CMAKE_C_COMPILER_ID': 'GNU',
            'CMAKE_BUILD_TYPE': 'Release',
            'CMAKE_INSTALL_PREFIX': '/usr/local',
        })
    
    def _extract_variables(self, content: str):
        """
        Extract variable definitions from CMake content.
        
        Args:
            content: CMake content as string
        """
        # First pass: extract all variable definitions without resolving
        raw_variables = {}
        set_matches = self.re_set.finditer(content)
        for match in set_matches:
            var_name = match.group(1)
            var_value_str = match.group(2) if match.group(2) else ''
            
            # Parse the variable value, handling multiple arguments
            var_args = self._parse_arguments(var_value_str)
            
            # Handle different set() command formats
            if not var_args:
                # Empty set() - set the variable to empty string
                raw_variables[var_name] = ''
            elif len(var_args) == 1:
                # Single value - store as-is for now
                raw_variables[var_name] = var_args[0]
            else:
                # Multiple values - join with semicolons (CMake list format)
                raw_variables[var_name] = ';'.join(var_args)
        
        # Second pass: resolve variables in order of definition
        for var_name, var_value in raw_variables.items():
            if var_value:
                # Resolve variables in the value
                resolved_value = self._resolve_variables(var_value)
                self.variables[var_name] = resolved_value
            else:
                # Empty value
                self.variables[var_name] = ''
    
    def _resolve_variables(self, content: str) -> str:
        """
        Resolve variable references in CMake content.
        
        Args:
            content: CMake content with variable references
            
        Returns:
            Content with variables resolved
        """
        # Handle nested variable resolution by finding and resolving from innermost to outermost
        resolved_content = content
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            # Find all variable references, including nested ones
            var_refs = self._find_variable_references(resolved_content)
            if not var_refs:
                break
                
            # Replace variables from innermost to outermost
            for start, end, var_name in reversed(var_refs):
                # Resolve the variable name (in case it contains other variables)
                resolved_var_name = self._resolve_variables(var_name) if '${' in var_name else var_name
                
                # Look up the variable value
                if resolved_var_name in self.variables:
                    var_value = self.variables[resolved_var_name]
                else:
                    # Variable not found - return empty string (CMake behavior)
                    var_value = ''
                
                # Replace the variable reference with its value
                resolved_content = resolved_content[:start] + var_value + resolved_content[end:]
            
            iteration += 1
        
        return resolved_content
    
    def _find_variable_references(self, content: str) -> List[Tuple[int, int, str]]:
        """
        Find all variable references in content, handling nested variables.
        
        Args:
            content: Content to search for variable references
            
        Returns:
            List of tuples (start_pos, end_pos, var_name) for each variable reference
        """
        references = []
        i = 0
        
        while i < len(content):
            # Look for ${
            if i < len(content) - 1 and content[i:i+2] == '${':
                start_pos = i
                i += 2
                brace_count = 1
                var_start = i
                
                # Find the matching closing brace, handling nested braces
                while i < len(content) and brace_count > 0:
                    if content[i] == '{':
                        brace_count += 1
                    elif content[i] == '}':
                        brace_count -= 1
                    i += 1
                
                if brace_count == 0:
                    # Found complete variable reference
                    end_pos = i
                    var_name = content[var_start:i-1]  # Exclude the closing }
                    references.append((start_pos, end_pos, var_name))
                else:
                    # Unmatched braces, skip
                    i = start_pos + 1
            else:
                i += 1
        
        return references
    
    def _process_conditional_statements(self, content: str) -> str:
        """
        Process conditional statements (if/elseif/else/endif) in CMake content.
        
        This method evaluates conditional blocks and returns the content with
        only the active branches included. For simplicity, this implementation
        assumes all conditions are true (basic implementation).
        
        Args:
            content: CMake content as string
            
        Returns:
            Processed content with conditional statements evaluated
        """
        lines = content.split('\n')
        result_lines = []
        
        # Stack to track nested conditional blocks
        # Each element is a dict with: {'type': 'if'|'elseif'|'else', 'condition': str, 'active': bool}
        conditional_stack = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for if statement
            if_match = self.re_if.match(line)
            if if_match:
                condition = if_match.group(1)
                # For basic implementation, evaluate simple conditions
                is_active = self._evaluate_condition(condition)
                conditional_stack.append({
                    'type': 'if',
                    'condition': condition,
                    'active': is_active,
                    'has_executed': is_active  # Track if any branch has been executed
                })
                i += 1
                continue
            
            # Check for elseif statement
            elseif_match = self.re_elseif.match(line)
            if elseif_match and conditional_stack:
                condition = elseif_match.group(1)
                current_block = conditional_stack[-1]
                
                # Only evaluate elseif if no previous branch was executed
                if not current_block['has_executed']:
                    is_active = self._evaluate_condition(condition)
                    current_block['active'] = is_active
                    current_block['has_executed'] = is_active
                else:
                    current_block['active'] = False
                
                current_block['type'] = 'elseif'
                current_block['condition'] = condition
                i += 1
                continue
            
            # Check for else statement
            else_match = self.re_else.match(line)
            if else_match and conditional_stack:
                current_block = conditional_stack[-1]
                
                # Only activate else if no previous branch was executed
                current_block['active'] = not current_block['has_executed']
                current_block['type'] = 'else'
                i += 1
                continue
            
            # Check for endif statement
            endif_match = self.re_endif.match(line)
            if endif_match and conditional_stack:
                conditional_stack.pop()
                i += 1
                continue
            
            # Regular line - include it if we're in an active block or no conditional block
            should_include = True
            if conditional_stack:
                # Check if all nested conditional blocks are active
                should_include = all(block['active'] for block in conditional_stack)
            
            if should_include:
                result_lines.append(lines[i])
            
            i += 1
        
        return '\n'.join(result_lines)
    
    def _evaluate_condition(self, condition: str) -> bool:
        """
        Evaluate a CMake conditional expression.
        
        This is a basic implementation that handles simple conditions.
        For a full implementation, this would need to handle CMake variables,
        operators, and complex expressions.
        
        Args:
            condition: The condition string to evaluate
            
        Returns:
            True if the condition is considered true, False otherwise
        """
        condition = condition.strip()
        
        # Handle empty conditions
        if not condition:
            return False
        
        # Handle simple boolean values
        if condition.upper() in ['TRUE', 'ON', 'YES', '1']:
            return True
        if condition.upper() in ['FALSE', 'OFF', 'NO', '0', '']:
            return False
        
        # Handle NOT operator
        if condition.upper().startswith('NOT '):
            inner_condition = condition[4:].strip()
            return not self._evaluate_condition(inner_condition)
        
        # Handle DEFINED operator
        if condition.upper().startswith('DEFINED '):
            # For basic implementation, assume variables are defined
            return True
        
        # Handle string comparisons (basic)
        if ' STREQUAL ' in condition.upper():
            parts = condition.split()
            if len(parts) >= 3:
                # Basic string equality check
                left = parts[0].strip('"\'')
                right = parts[2].strip('"\'')
                return left == right
        
        # Handle version comparisons (basic)
        if any(op in condition.upper() for op in [' VERSION_GREATER ', ' VERSION_LESS ', ' VERSION_EQUAL ']):
            # For basic implementation, assume version conditions are true
            return True
        
        # Handle EXISTS operator
        if condition.upper().startswith('EXISTS '):
            # For basic implementation, assume files exist
            return True
        
        # Handle variable references (basic)
        if condition.startswith('${') and condition.endswith('}'):
            # For basic implementation, assume variables are truthy
            return True
        
        # Handle simple variable names
        if condition.isalnum() or '_' in condition:
            # For basic implementation, assume variables are truthy
            return True
        
        # Default to true for unknown conditions (conservative approach)
        return True
    
    def _normalize_multiline_commands(self, content: str) -> str:
        """
        Normalize multi-line CMake commands by removing newlines within parentheses.
        
        This method handles comments properly by preserving comment boundaries.
        
        Args:
            content: CMake content as string
            
        Returns:
            Normalized content with newlines removed within parentheses
        """
        result = []
        paren_level = 0
        in_comment = False
        i = 0
        
        while i < len(content):
            char = content[i]
            
            if char == '(':
                paren_level += 1
                result.append(char)
                in_comment = False
            elif char == ')':
                paren_level -= 1
                result.append(char)
                in_comment = False
            elif char == '#' and paren_level > 0:
                # Start of comment within parentheses
                in_comment = True
                result.append(char)
            elif char in ['\n', '\r']:
                if paren_level > 0:
                    if in_comment:
                        # End of comment - preserve the newline to terminate the comment
                        result.append(char)
                        in_comment = False
                    else:
                        # Replace newlines within parentheses with spaces (but not in comments)
                        result.append(' ')
                else:
                    result.append(char)
            else:
                result.append(char)
            
            i += 1
        
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
        quote_char = None
        i = 0
        
        while i < len(args_str):
            char = args_str[i]
            
            # Handle comments - skip everything after # until end of line or end of string
            if char == '#' and not in_quotes:
                # Add current argument if we have one
                if current_arg.strip():
                    args.append(current_arg.strip())
                    current_arg = ''
                
                # Skip to the end of the line or end of string
                while i < len(args_str) and args_str[i] not in ['\n', '\r']:
                    i += 1
                
                # Continue processing after the newline
                if i < len(args_str):
                    i += 1
                continue
            
            # Handle quotes (both single and double)
            if char in ['"', "'"] and (not current_arg or current_arg[-1] != '\\'):
                if not in_quotes:
                    # Starting a quoted string
                    in_quotes = True
                    quote_char = char
                    current_arg += char
                elif char == quote_char:
                    # Ending the quoted string
                    in_quotes = False
                    quote_char = None
                    current_arg += char
                else:
                    # Different quote character inside quotes
                    current_arg += char
            elif char.isspace() and not in_quotes:
                if current_arg.strip():
                    args.append(current_arg.strip())
                    current_arg = ''
            else:
                current_arg += char
            
            i += 1
        
        if current_arg.strip():
            args.append(current_arg.strip())
        
        # Clean up arguments (remove quotes, extra whitespace)
        cleaned_args = []
        for arg in args:
            if arg:
                # Remove surrounding quotes if present
                if (arg.startswith('"') and arg.endswith('"')) or \
                   (arg.startswith("'") and arg.endswith("'")):
                    arg = arg[1:-1]
                cleaned_args.append(arg)
        
        return cleaned_args
    
    def _parse_target_link_libraries_dependencies(self, dependencies_str: str) -> Dict[str, List[str]]:
        """
        Parse dependencies from target_link_libraries command with scope handling.
        
        Args:
            dependencies_str: String containing dependencies and optional scope keywords
            
        Returns:
            Dictionary with dependencies organized by scope (INTERFACE, PUBLIC, PRIVATE)
        """
        # Initialize result with all scopes
        result = {
            'INTERFACE': [],
            'PUBLIC': [],
            'PRIVATE': []
        }
        
        # Parse arguments
        args = self._parse_arguments(dependencies_str)
        
        # Current scope - defaults to PRIVATE if no scope is specified
        current_scope = 'PRIVATE'
        
        for arg in args:
            # Check if this argument is a scope keyword
            if arg in ['INTERFACE', 'PUBLIC', 'PRIVATE']:
                current_scope = arg
            else:
                # This is a dependency, add it to the current scope
                result[current_scope].append(arg)
        
        return result
    
    def _process_custom_commands_and_macros(self, content: str):
        """
        Process custom commands and macros in CMake content.
        
        Args:
            content: CMake content as string
        """
        # Process add_custom_command
        custom_command_matches = self.re_add_custom_command.finditer(content)
        for match in custom_command_matches:
            args_str = match.group(1)
            self._handle_add_custom_command(args_str)
        
        # Process add_custom_target
        custom_target_matches = self.re_add_custom_target.finditer(content)
        for match in custom_target_matches:
            target_name = match.group(1)
            args_str = match.group(2) if match.group(2) else ''
            self._handle_add_custom_target(target_name, args_str)
        
        # Process macro definitions
        self._process_macro_definitions(content)
        
        # Process function definitions
        self._process_function_definitions(content)
    
    def _handle_add_custom_command(self, args_str: str):
        """
        Handle add_custom_command.
        
        Args:
            args_str: Arguments string for the custom command
        """
        args = self._parse_arguments(args_str)
        
        custom_command = {
            'type': 'add_custom_command',
            'args': args,
            'output': [],
            'command': [],
            'depends': [],
            'working_directory': None,
            'comment': None,
            'warning': None
        }
        
        # Parse common add_custom_command patterns
        i = 0
        while i < len(args):
            arg = args[i]
            
            if arg == 'OUTPUT':
                # Collect output files
                i += 1
                while i < len(args) and args[i] not in ['COMMAND', 'DEPENDS', 'WORKING_DIRECTORY', 'COMMENT']:
                    custom_command['output'].append(args[i])
                    i += 1
                continue
            elif arg == 'COMMAND':
                # Collect command and arguments
                i += 1
                command_parts = []
                while i < len(args) and args[i] not in ['OUTPUT', 'DEPENDS', 'WORKING_DIRECTORY', 'COMMENT']:
                    command_parts.append(args[i])
                    i += 1
                custom_command['command'].extend(command_parts)
                continue
            elif arg == 'DEPENDS':
                # Collect dependencies
                i += 1
                while i < len(args) and args[i] not in ['OUTPUT', 'COMMAND', 'WORKING_DIRECTORY', 'COMMENT']:
                    custom_command['depends'].append(args[i])
                    i += 1
                continue
            elif arg == 'WORKING_DIRECTORY':
                # Set working directory
                i += 1
                if i < len(args):
                    custom_command['working_directory'] = args[i]
                    i += 1
                continue
            elif arg == 'COMMENT':
                # Set comment
                i += 1
                if i < len(args):
                    custom_command['comment'] = args[i]
                    i += 1
                continue
            
            i += 1
        
        # Add warning for unsupported features
        if not custom_command['output'] and not custom_command['command']:
            custom_command['warning'] = 'Custom command has no OUTPUT or COMMAND - may not be fully supported in Bazel'
        elif custom_command['command']:
            custom_command['warning'] = 'Custom commands require manual conversion to Bazel genrule or custom rule'
        
        self.custom_commands.append(custom_command)
    
    def _handle_add_custom_target(self, target_name: str, args_str: str):
        """
        Handle add_custom_target.
        
        Args:
            target_name: Name of the custom target
            args_str: Arguments string for the custom target
        """
        args = self._parse_arguments(args_str)
        
        custom_target = {
            'type': 'add_custom_target',
            'name': target_name,
            'args': args,
            'command': [],
            'depends': [],
            'working_directory': None,
            'comment': None,
            'all': False,
            'warning': 'Custom targets require manual conversion to Bazel rules'
        }
        
        # Parse common add_custom_target patterns
        i = 0
        while i < len(args):
            arg = args[i]
            
            if arg == 'ALL':
                custom_target['all'] = True
                i += 1
                continue
            elif arg == 'COMMAND':
                # Collect command and arguments
                i += 1
                command_parts = []
                while i < len(args) and args[i] not in ['DEPENDS', 'WORKING_DIRECTORY', 'COMMENT']:
                    command_parts.append(args[i])
                    i += 1
                custom_target['command'].extend(command_parts)
                continue
            elif arg == 'DEPENDS':
                # Collect dependencies
                i += 1
                while i < len(args) and args[i] not in ['COMMAND', 'WORKING_DIRECTORY', 'COMMENT']:
                    custom_target['depends'].append(args[i])
                    i += 1
                continue
            elif arg == 'WORKING_DIRECTORY':
                # Set working directory
                i += 1
                if i < len(args):
                    custom_target['working_directory'] = args[i]
                    i += 1
                continue
            elif arg == 'COMMENT':
                # Set comment
                i += 1
                if i < len(args):
                    custom_target['comment'] = args[i]
                    i += 1
                continue
            else:
                # First non-keyword argument is typically the command
                if not custom_target['command']:
                    custom_target['command'].append(arg)
                i += 1
        
        self.custom_targets.append(custom_target)
    
    def _process_macro_definitions(self, content: str):
        """
        Process macro definitions in CMake content.
        
        Args:
            content: CMake content as string
        """
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for macro definition
            macro_match = self.re_macro.match(line)
            if macro_match:
                macro_name = macro_match.group(1)
                macro_args = macro_match.group(2) if macro_match.group(2) else ''
                
                # Collect macro body until endmacro
                macro_body = []
                i += 1
                
                while i < len(lines):
                    body_line = lines[i].strip()
                    
                    # Check for endmacro
                    if self.re_endmacro.match(body_line):
                        break
                    
                    macro_body.append(lines[i])
                    i += 1
                
                # Store macro definition
                self.custom_macros[macro_name] = {
                    'name': macro_name,
                    'args': self._parse_arguments(macro_args) if macro_args else [],
                    'body': '\n'.join(macro_body),
                    'warning': f'Macro "{macro_name}" requires manual conversion - macros are not directly supported in Bazel'
                }
            
            i += 1
    
    def _process_function_definitions(self, content: str):
        """
        Process function definitions in CMake content.
        
        Args:
            content: CMake content as string
        """
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for function definition
            function_match = self.re_function.match(line)
            if function_match:
                function_name = function_match.group(1)
                function_args = function_match.group(2) if function_match.group(2) else ''
                
                # Collect function body until endfunction
                function_body = []
                i += 1
                
                while i < len(lines):
                    body_line = lines[i].strip()
                    
                    # Check for endfunction
                    if self.re_endfunction.match(body_line):
                        break
                    
                    function_body.append(lines[i])
                    i += 1
                
                # Store function definition
                self.custom_functions[function_name] = {
                    'name': function_name,
                    'args': self._parse_arguments(function_args) if function_args else [],
                    'body': '\n'.join(function_body),
                    'warning': f'Function "{function_name}" requires manual conversion - functions are not directly supported in Bazel'
                }
            
            i += 1
    
    def _handle_macro_definition(self, args_str: str):
        """
        Handle macro definition (legacy method for compatibility).
        
        Args:
            args_str: Arguments string for the macro
        """
        # This method is kept for compatibility with the mapping system
        # The actual processing is done in _process_macro_definitions
        pass
    
    def _handle_function_definition(self, args_str: str):
        """
        Handle function definition (legacy method for compatibility).
        
        Args:
            args_str: Arguments string for the function
        """
        # This method is kept for compatibility with the mapping system
        # The actual processing is done in _process_function_definitions
        pass


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