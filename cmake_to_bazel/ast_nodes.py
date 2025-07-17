# cmake_to_bazel/ast_nodes.py

from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod


class ASTNode(ABC):
    """
    Abstract base class for all AST nodes.
    
    This class defines the common interface that all AST nodes must implement.
    """
    
    def __init__(self, node_type: str):
        """
        Initialize the AST node.
        
        Args:
            node_type: The type of the AST node
        """
        self.node_type = node_type
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the AST node to a dictionary representation.
        
        Returns:
            Dictionary representation of the AST node
        """
        pass
    
    def __repr__(self) -> str:
        """Return string representation of the node."""
        return f"{self.__class__.__name__}({self.to_dict()})"


class ProjectNode(ASTNode):
    """AST node representing a CMake project."""
    
    def __init__(self, name: str, minimum_required_version: Optional[str] = None):
        """
        Initialize the project node.
        
        Args:
            name: Project name
            minimum_required_version: Minimum required CMake version
        """
        super().__init__('project')
        self.name = name
        self.minimum_required_version = minimum_required_version
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'type': self.node_type,
            'name': self.name,
            'minimum_required_version': self.minimum_required_version
        }


class IncludeDirectoryNode(ASTNode):
    """AST node representing an include directory."""
    
    def __init__(self, path: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize the include directory node.
        
        Args:
            path: Path to the include directory
            metadata: Optional metadata (e.g., SYSTEM, BEFORE, AFTER)
        """
        super().__init__('include_directory')
        self.path = path
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            'type': self.node_type,
            'path': self.path
        }
        if self.metadata:
            result['metadata'] = self.metadata
        return result


class SourceFileNode(ASTNode):
    """AST node representing a source file."""
    
    def __init__(self, path: str, file_type: Optional[str] = None):
        """
        Initialize the source file node.
        
        Args:
            path: Path to the source file
            file_type: Optional file type (e.g., 'cpp', 'c', 'h')
        """
        super().__init__('source_file')
        self.path = path
        self.file_type = file_type or self._infer_file_type(path)
    
    def _infer_file_type(self, path: str) -> str:
        """
        Infer file type from file extension.
        
        Args:
            path: File path
            
        Returns:
            Inferred file type
        """
        if '.' not in path:
            return 'unknown'
        
        extension = path.split('.')[-1].lower()
        type_mapping = {
            'cpp': 'cpp',
            'cxx': 'cpp',
            'cc': 'cpp',
            'c': 'c',
            'h': 'header',
            'hpp': 'header',
            'hxx': 'header',
            'hh': 'header'
        }
        return type_mapping.get(extension, 'unknown')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'type': self.node_type,
            'path': self.path,
            'file_type': self.file_type
        }


class DependencyNode(ASTNode):
    """AST node representing a target dependency."""
    
    def __init__(self, name: str, scope: str = 'PRIVATE', dependency_type: str = 'library'):
        """
        Initialize the dependency node.
        
        Args:
            name: Name of the dependency
            scope: Dependency scope (PRIVATE, PUBLIC, INTERFACE)
            dependency_type: Type of dependency (library, system, etc.)
        """
        super().__init__('dependency')
        self.name = name
        self.scope = scope
        self.dependency_type = dependency_type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'type': self.node_type,
            'name': self.name,
            'scope': self.scope,
            'dependency_type': self.dependency_type
        }


class TargetIncludeDirectoryNode(ASTNode):
    """AST node representing a target-specific include directory."""
    
    def __init__(self, path: str, scope: str = 'PRIVATE', metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize the target include directory node.
        
        Args:
            path: Path to the include directory
            scope: Include scope (PRIVATE, PUBLIC, INTERFACE)
            metadata: Optional metadata (e.g., SYSTEM, BEFORE, AFTER)
        """
        super().__init__('target_include_directory')
        self.path = path
        self.scope = scope
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            'type': self.node_type,
            'path': self.path,
            'scope': self.scope
        }
        if self.metadata:
            result['metadata'] = self.metadata
        return result


class TargetNode(ASTNode):
    """AST node representing a CMake target (executable or library)."""
    
    def __init__(self, name: str, target_type: str, sources: Optional[List[SourceFileNode]] = None,
                 dependencies: Optional[List[DependencyNode]] = None,
                 include_directories: Optional[List[TargetIncludeDirectoryNode]] = None,
                 compile_definitions: Optional[List[str]] = None,
                 compile_options: Optional[List[str]] = None,
                 **kwargs):
        """
        Initialize the target node.
        
        Args:
            name: Target name
            target_type: Type of target ('executable' or 'library')
            sources: List of source file nodes
            dependencies: List of dependency nodes
            include_directories: List of target include directory nodes
            compile_definitions: List of compile definitions
            compile_options: List of compile options
            **kwargs: Additional target-specific attributes
        """
        super().__init__('target')
        self.name = name
        self.target_type = target_type
        self.sources = sources or []
        self.dependencies = dependencies or []
        self.include_directories = include_directories or []
        self.compile_definitions = compile_definitions or []
        self.compile_options = compile_options or []
        
        # Store additional attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def add_source(self, source: SourceFileNode):
        """Add a source file to the target."""
        self.sources.append(source)
    
    def add_dependency(self, dependency: DependencyNode):
        """Add a dependency to the target."""
        self.dependencies.append(dependency)
    
    def add_include_directory(self, include_dir: TargetIncludeDirectoryNode):
        """Add an include directory to the target."""
        self.include_directories.append(include_dir)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            'type': self.node_type,
            'target_type': self.target_type,
            'name': self.name,
            'sources': [source.to_dict() for source in self.sources],
            'dependencies': [dep.to_dict() for dep in self.dependencies],
            'include_directories': [inc.to_dict() for inc in self.include_directories],
            'compile_definitions': self.compile_definitions,
            'compile_options': self.compile_options
        }
        
        # Add additional attributes
        for attr_name in dir(self):
            if not attr_name.startswith('_') and attr_name not in [
                'node_type', 'name', 'target_type', 'sources', 'dependencies',
                'include_directories', 'compile_definitions', 'compile_options',
                'add_source', 'add_dependency', 'add_include_directory', 'to_dict'
            ]:
                attr_value = getattr(self, attr_name)
                if not callable(attr_value):
                    result[attr_name] = attr_value
        
        return result


class ExecutableTargetNode(TargetNode):
    """AST node representing a CMake executable target."""
    
    def __init__(self, name: str, sources: Optional[List[SourceFileNode]] = None,
                 options: Optional[str] = None, **kwargs):
        """
        Initialize the executable target node.
        
        Args:
            name: Executable name
            sources: List of source file nodes
            options: Optional executable options (WIN32, MACOSX_BUNDLE, etc.)
            **kwargs: Additional attributes
        """
        super().__init__(name, 'executable', sources, **kwargs)
        self.options = options


class LibraryTargetNode(TargetNode):
    """AST node representing a CMake library target."""
    
    def __init__(self, name: str, library_type: str = 'STATIC',
                 sources: Optional[List[SourceFileNode]] = None,
                 library_specifier: Optional[str] = None, **kwargs):
        """
        Initialize the library target node.
        
        Args:
            name: Library name
            library_type: Type of library (STATIC, SHARED, MODULE, INTERFACE, OBJECT)
            sources: List of source file nodes
            library_specifier: Optional library specifier (IMPORTED, ALIAS, INTERFACE)
            **kwargs: Additional attributes
        """
        super().__init__(name, 'library', sources, **kwargs)
        self.library_type = library_type
        self.library_specifier = library_specifier


class VariableNode(ASTNode):
    """AST node representing a CMake variable."""
    
    def __init__(self, name: str, value: str, variable_type: str = 'string'):
        """
        Initialize the variable node.
        
        Args:
            name: Variable name
            value: Variable value
            variable_type: Type of variable (string, list, bool, etc.)
        """
        super().__init__('variable')
        self.name = name
        self.value = value
        self.variable_type = variable_type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'type': self.node_type,
            'name': self.name,
            'value': self.value,
            'variable_type': self.variable_type
        }


class CustomCommandNode(ASTNode):
    """AST node representing a custom CMake command."""
    
    def __init__(self, command: Dict[str, Any]):
        """
        Initialize the custom command node.
        
        Args:
            command: Dictionary containing command information
        """
        super().__init__('custom_command')
        self.command = command
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'type': self.node_type,
            'command': self.command
        }


class CustomTargetNode(ASTNode):
    """AST node representing a custom CMake target."""
    
    def __init__(self, target: Dict[str, Any]):
        """
        Initialize the custom target node.
        
        Args:
            target: Dictionary containing target information
        """
        super().__init__('custom_target')
        self.target = target
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'type': self.node_type,
            'target': self.target
        }


class CustomMacroNode(ASTNode):
    """AST node representing a custom CMake macro."""
    
    def __init__(self, name: str, data: Dict[str, Any]):
        """
        Initialize the custom macro node.
        
        Args:
            name: Macro name
            data: Dictionary containing macro information
        """
        super().__init__('custom_macro')
        self.name = name
        self.data = data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'type': self.node_type,
            'name': self.name,
            'data': self.data
        }


class CustomFunctionNode(ASTNode):
    """AST node representing a custom CMake function."""
    
    def __init__(self, name: str, data: Dict[str, Any]):
        """
        Initialize the custom function node.
        
        Args:
            name: Function name
            data: Dictionary containing function information
        """
        super().__init__('custom_function')
        self.name = name
        self.data = data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'type': self.node_type,
            'name': self.name,
            'data': self.data
        }


class CMakeAST:
    """
    Root AST class that contains all CMake constructs.
    
    This class represents the complete AST for a CMakeLists.txt file.
    """
    
    def __init__(self, project: Optional[ProjectNode] = None,
                 minimum_required_version: Optional[str] = None):
        """
        Initialize the CMake AST.
        
        Args:
            project: Project node
            minimum_required_version: Minimum required CMake version
        """
        self.project = project
        self.minimum_required_version = minimum_required_version
        self.include_directories: List[IncludeDirectoryNode] = []
        self.targets: List[TargetNode] = []
        self.variables: List[VariableNode] = []
        self.custom_commands: List[CustomCommandNode] = []
        self.custom_targets: List[CustomTargetNode] = []
        self.custom_macros: List[CustomMacroNode] = []
        self.custom_functions: List[CustomFunctionNode] = []
    
    def add_include_directory(self, include_dir: IncludeDirectoryNode):
        """Add an include directory to the AST."""
        self.include_directories.append(include_dir)
    
    def add_target(self, target: TargetNode):
        """Add a target to the AST."""
        self.targets.append(target)
    
    def add_variable(self, variable: VariableNode):
        """Add a variable to the AST."""
        self.variables.append(variable)
    
    def add_custom_command(self, command: CustomCommandNode):
        """Add a custom command to the AST."""
        self.custom_commands.append(command)
    
    def add_custom_target(self, target: CustomTargetNode):
        """Add a custom target to the AST."""
        self.custom_targets.append(target)
    
    def add_custom_macro(self, macro: CustomMacroNode):
        """Add a custom macro to the AST."""
        self.custom_macros.append(macro)
    
    def add_custom_function(self, function: CustomFunctionNode):
        """Add a custom function to the AST."""
        self.custom_functions.append(function)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the entire AST to a dictionary representation."""
        return {
            'project': self.project.to_dict() if self.project else None,
            'minimum_required_version': self.minimum_required_version,
            'include_directories': [inc.to_dict() for inc in self.include_directories],
            'targets': [target.to_dict() for target in self.targets],
            'variables': [var.to_dict() for var in self.variables],
            'custom_commands': [cmd.to_dict() for cmd in self.custom_commands],
            'custom_targets': [target.to_dict() for target in self.custom_targets],
            'custom_macros': [macro.to_dict() for macro in self.custom_macros],
            'custom_functions': [func.to_dict() for func in self.custom_functions]
        }