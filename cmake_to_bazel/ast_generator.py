# cmake_to_bazel/ast_generator.py

from typing import Dict, List, Any, Optional
from ast_nodes import (
    CMakeAST, ProjectNode, IncludeDirectoryNode, SourceFileNode,
    DependencyNode, TargetIncludeDirectoryNode, TargetNode,
    ExecutableTargetNode, LibraryTargetNode, VariableNode,
    CustomCommandNode, CustomTargetNode, CustomMacroNode, CustomFunctionNode
)


class ASTGenerator:
    """
    A generator that converts parsed CMake content into an Abstract Syntax Tree (AST).
    
    This class is responsible for transforming the dictionary representation of
    parsed CMake content into a structured AST that can be used by the Bazel
    rule generator.
    """
    
    def __init__(self):
        """Initialize the AST generator."""
        pass
    
    def generate_ast(self, parsed_content: Dict[str, Any]) -> CMakeAST:
        """
        Generate AST from parsed CMake content.
        
        Args:
            parsed_content: Dictionary with parsed CMake content
            
        Returns:
            CMakeAST object representing the AST
            
        Raises:
            ValueError: If the parsed content is invalid or missing required fields
        """
        if not isinstance(parsed_content, dict):
            raise ValueError("Parsed content must be a dictionary")
        
        # Create the root AST object
        project_node = self._create_project_node(parsed_content)
        ast = CMakeAST(
            project=project_node,
            minimum_required_version=parsed_content.get('minimum_required_version')
        )
        
        # Add all components to the AST
        for include_dir in self._create_include_directories_nodes(parsed_content):
            ast.add_include_directory(include_dir)
        
        for target in self._create_target_nodes(parsed_content):
            ast.add_target(target)
        
        for variable in self._create_variable_nodes(parsed_content):
            ast.add_variable(variable)
        
        for command in self._create_custom_command_nodes(parsed_content):
            ast.add_custom_command(command)
        
        for target in self._create_custom_target_nodes(parsed_content):
            ast.add_custom_target(target)
        
        for macro in self._create_custom_macro_nodes(parsed_content):
            ast.add_custom_macro(macro)
        
        for function in self._create_custom_function_nodes(parsed_content):
            ast.add_custom_function(function)
        
        return ast
    
    def _create_project_node(self, parsed_content: Dict[str, Any]) -> Optional[ProjectNode]:
        """
        Create a project node from parsed content.
        
        Args:
            parsed_content: Dictionary with parsed CMake content
            
        Returns:
            ProjectNode object or None if no project is defined
        """
        project_name = parsed_content.get('project')
        if not project_name:
            return None
        
        return ProjectNode(
            name=project_name,
            minimum_required_version=parsed_content.get('minimum_required_version')
        )
    
    def _create_include_directories_nodes(self, parsed_content: Dict[str, Any]) -> List[IncludeDirectoryNode]:
        """
        Create include directory nodes from parsed content.
        
        Args:
            parsed_content: Dictionary with parsed CMake content
            
        Returns:
            List of IncludeDirectoryNode objects
        """
        include_dirs = parsed_content.get('include_directories', [])
        include_dirs_metadata = parsed_content.get('include_directories_metadata', {})
        
        nodes = []
        for directory in include_dirs:
            metadata = include_dirs_metadata.get(directory)
            node = IncludeDirectoryNode(path=directory, metadata=metadata)
            nodes.append(node)
        
        return nodes
    
    def _create_target_nodes(self, parsed_content: Dict[str, Any]) -> List[TargetNode]:
        """
        Create target nodes from parsed content.
        
        Args:
            parsed_content: Dictionary with parsed CMake content
            
        Returns:
            List of TargetNode objects
        """
        targets = parsed_content.get('targets', [])
        nodes = []
        
        for target in targets:
            target_type = target.get('type')
            target_name = target.get('name')
            sources = self._create_source_nodes(target.get('sources', []))
            dependencies = self._create_dependency_nodes(target.get('dependencies', []))
            include_directories = self._create_target_include_directory_nodes(target)
            compile_definitions = target.get('compile_definitions', [])
            compile_options = target.get('compile_options', [])
            
            if target_type == 'executable':
                node = ExecutableTargetNode(
                    name=target_name,
                    sources=sources,
                    dependencies=dependencies,
                    include_directories=include_directories,
                    compile_definitions=compile_definitions,
                    compile_options=compile_options,
                    options=target.get('options')
                )
            elif target_type == 'library':
                node = LibraryTargetNode(
                    name=target_name,
                    library_type=target.get('library_type', 'STATIC'),
                    sources=sources,
                    dependencies=dependencies,
                    include_directories=include_directories,
                    compile_definitions=compile_definitions,
                    compile_options=compile_options,
                    library_specifier=target.get('library_specifier')
                )
            else:
                # Generic target node for unknown types
                node = TargetNode(
                    name=target_name,
                    target_type=target_type,
                    sources=sources,
                    dependencies=dependencies,
                    include_directories=include_directories,
                    compile_definitions=compile_definitions,
                    compile_options=compile_options
                )
            
            nodes.append(node)
        
        return nodes
    
    def _create_source_nodes(self, sources: List[str]) -> List[SourceFileNode]:
        """
        Create source file nodes from a list of source files.
        
        Args:
            sources: List of source file paths
            
        Returns:
            List of SourceFileNode objects
        """
        nodes = []
        for source in sources:
            nodes.append(SourceFileNode(path=source))
        return nodes
    
    def _create_dependency_nodes(self, dependencies: Any) -> List[DependencyNode]:
        """
        Create dependency nodes from dependencies data.
        
        Args:
            dependencies: Dependencies data (can be list or dict with scopes)
            
        Returns:
            List of DependencyNode objects
        """
        nodes = []
        
        if isinstance(dependencies, list):
            # Simple list of dependencies (legacy format)
            for dep in dependencies:
                nodes.append(DependencyNode(name=dep, scope='PRIVATE'))
        elif isinstance(dependencies, dict):
            # Scoped dependencies
            for scope, deps in dependencies.items():
                if scope in ['INTERFACE', 'PUBLIC', 'PRIVATE']:
                    for dep in deps:
                        nodes.append(DependencyNode(name=dep, scope=scope))
        
        return nodes
    
    def _create_target_include_directory_nodes(self, target: Dict[str, Any]) -> List[TargetIncludeDirectoryNode]:
        """
        Create target-specific include directory nodes.
        
        Args:
            target: Target dictionary from parsed content
            
        Returns:
            List of TargetIncludeDirectoryNode objects
        """
        nodes = []
        include_dirs = target.get('include_directories', {})
        include_dirs_metadata = target.get('include_directories_metadata', {})
        
        if isinstance(include_dirs, dict):
            # Scoped include directories
            for scope, dirs in include_dirs.items():
                if scope in ['INTERFACE', 'PUBLIC', 'PRIVATE']:
                    for directory in dirs:
                        metadata = include_dirs_metadata.get(directory)
                        node = TargetIncludeDirectoryNode(
                            path=directory,
                            scope=scope,
                            metadata=metadata
                        )
                        nodes.append(node)
        elif isinstance(include_dirs, list):
            # Legacy format - treat as PRIVATE
            for directory in include_dirs:
                metadata = include_dirs_metadata.get(directory)
                node = TargetIncludeDirectoryNode(
                    path=directory,
                    scope='PRIVATE',
                    metadata=metadata
                )
                nodes.append(node)
        
        return nodes
    
    def _create_variable_nodes(self, parsed_content: Dict[str, Any]) -> List[VariableNode]:
        """
        Create variable nodes from parsed content.
        
        Args:
            parsed_content: Dictionary with parsed CMake content
            
        Returns:
            List of VariableNode objects
        """
        variables = parsed_content.get('variables', {})
        nodes = []
        
        for name, value in variables.items():
            # Determine variable type based on value
            variable_type = 'string'
            if isinstance(value, str) and ';' in value:
                variable_type = 'list'
            elif isinstance(value, bool):
                variable_type = 'bool'
            elif isinstance(value, (int, float)):
                variable_type = 'number'
            
            nodes.append(VariableNode(name=name, value=str(value), variable_type=variable_type))
        
        return nodes
    
    def _create_custom_command_nodes(self, parsed_content: Dict[str, Any]) -> List[CustomCommandNode]:
        """
        Create custom command nodes from parsed content.
        
        Args:
            parsed_content: Dictionary with parsed CMake content
            
        Returns:
            List of CustomCommandNode objects
        """
        custom_commands = parsed_content.get('custom_commands', [])
        nodes = []
        
        for command in custom_commands:
            nodes.append(CustomCommandNode(command=command))
        
        return nodes
    
    def _create_custom_target_nodes(self, parsed_content: Dict[str, Any]) -> List[CustomTargetNode]:
        """
        Create custom target nodes from parsed content.
        
        Args:
            parsed_content: Dictionary with parsed CMake content
            
        Returns:
            List of CustomTargetNode objects
        """
        custom_targets = parsed_content.get('custom_targets', [])
        nodes = []
        
        for target in custom_targets:
            nodes.append(CustomTargetNode(target=target))
        
        return nodes
    
    def _create_custom_macro_nodes(self, parsed_content: Dict[str, Any]) -> List[CustomMacroNode]:
        """
        Create custom macro nodes from parsed content.
        
        Args:
            parsed_content: Dictionary with parsed CMake content
            
        Returns:
            List of CustomMacroNode objects
        """
        custom_macros = parsed_content.get('custom_macros', {})
        nodes = []
        
        for name, macro_data in custom_macros.items():
            nodes.append(CustomMacroNode(name=name, data=macro_data))
        
        return nodes
    
    def _create_custom_function_nodes(self, parsed_content: Dict[str, Any]) -> List[CustomFunctionNode]:
        """
        Create custom function nodes from parsed content.
        
        Args:
            parsed_content: Dictionary with parsed CMake content
            
        Returns:
            List of CustomFunctionNode objects
        """
        custom_functions = parsed_content.get('custom_functions', {})
        nodes = []
        
        for name, function_data in custom_functions.items():
            nodes.append(CustomFunctionNode(name=name, data=function_data))
        
        return nodes