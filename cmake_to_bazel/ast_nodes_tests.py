# cmake_to_bazel/ast_nodes_tests.py

import unittest
from ast_nodes import (
    ProjectNode, IncludeDirectoryNode, SourceFileNode, DependencyNode,
    TargetIncludeDirectoryNode, TargetNode, ExecutableTargetNode,
    LibraryTargetNode, VariableNode, CustomCommandNode, CustomTargetNode,
    CustomMacroNode, CustomFunctionNode, CMakeAST
)


class TestProjectNode(unittest.TestCase):
    """Test cases for the ProjectNode class."""
    
    def test_project_node_creation(self):
        """Test project node creation with basic parameters."""
        node = ProjectNode(name="TestProject", minimum_required_version="3.10")
        
        self.assertEqual(node.node_type, 'project')
        self.assertEqual(node.name, "TestProject")
        self.assertEqual(node.minimum_required_version, "3.10")
    
    def test_project_node_to_dict(self):
        """Test project node dictionary conversion."""
        node = ProjectNode(name="TestProject", minimum_required_version="3.10")
        result = node.to_dict()
        
        expected = {
            'type': 'project',
            'name': 'TestProject',
            'minimum_required_version': '3.10'
        }
        self.assertEqual(result, expected)
    
    def test_project_node_without_version(self):
        """Test project node creation without minimum required version."""
        node = ProjectNode(name="TestProject")
        
        self.assertEqual(node.name, "TestProject")
        self.assertIsNone(node.minimum_required_version)


class TestIncludeDirectoryNode(unittest.TestCase):
    """Test cases for the IncludeDirectoryNode class."""
    
    def test_include_directory_node_creation(self):
        """Test include directory node creation."""
        node = IncludeDirectoryNode(path="include", metadata={'system': True})
        
        self.assertEqual(node.node_type, 'include_directory')
        self.assertEqual(node.path, "include")
        self.assertEqual(node.metadata, {'system': True})
    
    def test_include_directory_node_to_dict(self):
        """Test include directory node dictionary conversion."""
        node = IncludeDirectoryNode(path="include", metadata={'system': True})
        result = node.to_dict()
        
        expected = {
            'type': 'include_directory',
            'path': 'include',
            'metadata': {'system': True}
        }
        self.assertEqual(result, expected)
    
    def test_include_directory_node_without_metadata(self):
        """Test include directory node creation without metadata."""
        node = IncludeDirectoryNode(path="include")
        
        self.assertEqual(node.path, "include")
        self.assertEqual(node.metadata, {})


class TestSourceFileNode(unittest.TestCase):
    """Test cases for the SourceFileNode class."""
    
    def test_source_file_node_creation(self):
        """Test source file node creation."""
        node = SourceFileNode(path="main.cpp")
        
        self.assertEqual(node.node_type, 'source_file')
        self.assertEqual(node.path, "main.cpp")
        self.assertEqual(node.file_type, "cpp")
    
    def test_source_file_node_to_dict(self):
        """Test source file node dictionary conversion."""
        node = SourceFileNode(path="main.cpp")
        result = node.to_dict()
        
        expected = {
            'type': 'source_file',
            'path': 'main.cpp',
            'file_type': 'cpp'
        }
        self.assertEqual(result, expected)
    
    def test_file_type_inference(self):
        """Test file type inference from extensions."""
        test_cases = [
            ("main.cpp", "cpp"),
            ("utils.cxx", "cpp"),
            ("lib.cc", "cpp"),
            ("source.c", "c"),
            ("header.h", "header"),
            ("header.hpp", "header"),
            ("header.hxx", "header"),
            ("header.hh", "header"),
            ("unknown.xyz", "unknown"),
            ("noextension", "unknown")
        ]
        
        for path, expected_type in test_cases:
            with self.subTest(path=path):
                node = SourceFileNode(path=path)
                self.assertEqual(node.file_type, expected_type)
    
    def test_explicit_file_type(self):
        """Test source file node creation with explicit file type."""
        node = SourceFileNode(path="main.cpp", file_type="custom")
        
        self.assertEqual(node.file_type, "custom")


class TestDependencyNode(unittest.TestCase):
    """Test cases for the DependencyNode class."""
    
    def test_dependency_node_creation(self):
        """Test dependency node creation."""
        node = DependencyNode(name="mylib", scope="PUBLIC", dependency_type="library")
        
        self.assertEqual(node.node_type, 'dependency')
        self.assertEqual(node.name, "mylib")
        self.assertEqual(node.scope, "PUBLIC")
        self.assertEqual(node.dependency_type, "library")
    
    def test_dependency_node_to_dict(self):
        """Test dependency node dictionary conversion."""
        node = DependencyNode(name="mylib", scope="PUBLIC", dependency_type="library")
        result = node.to_dict()
        
        expected = {
            'type': 'dependency',
            'name': 'mylib',
            'scope': 'PUBLIC',
            'dependency_type': 'library'
        }
        self.assertEqual(result, expected)
    
    def test_dependency_node_defaults(self):
        """Test dependency node creation with default values."""
        node = DependencyNode(name="mylib")
        
        self.assertEqual(node.scope, "PRIVATE")
        self.assertEqual(node.dependency_type, "library")


class TestTargetIncludeDirectoryNode(unittest.TestCase):
    """Test cases for the TargetIncludeDirectoryNode class."""
    
    def test_target_include_directory_node_creation(self):
        """Test target include directory node creation."""
        node = TargetIncludeDirectoryNode(
            path="include", 
            scope="PUBLIC", 
            metadata={'system': True}
        )
        
        self.assertEqual(node.node_type, 'target_include_directory')
        self.assertEqual(node.path, "include")
        self.assertEqual(node.scope, "PUBLIC")
        self.assertEqual(node.metadata, {'system': True})
    
    def test_target_include_directory_node_to_dict(self):
        """Test target include directory node dictionary conversion."""
        node = TargetIncludeDirectoryNode(
            path="include", 
            scope="PUBLIC", 
            metadata={'system': True}
        )
        result = node.to_dict()
        
        expected = {
            'type': 'target_include_directory',
            'path': 'include',
            'scope': 'PUBLIC',
            'metadata': {'system': True}
        }
        self.assertEqual(result, expected)
    
    def test_target_include_directory_node_defaults(self):
        """Test target include directory node creation with default values."""
        node = TargetIncludeDirectoryNode(path="include")
        
        self.assertEqual(node.scope, "PRIVATE")
        self.assertEqual(node.metadata, {})


class TestTargetNode(unittest.TestCase):
    """Test cases for the TargetNode class."""
    
    def test_target_node_creation(self):
        """Test target node creation."""
        sources = [SourceFileNode("main.cpp")]
        dependencies = [DependencyNode("mylib")]
        includes = [TargetIncludeDirectoryNode("include")]
        
        node = TargetNode(
            name="mytarget",
            target_type="executable",
            sources=sources,
            dependencies=dependencies,
            include_directories=includes,
            compile_definitions=["DEBUG"],
            compile_options=["-O2"]
        )
        
        self.assertEqual(node.node_type, 'target')
        self.assertEqual(node.name, "mytarget")
        self.assertEqual(node.target_type, "executable")
        self.assertEqual(len(node.sources), 1)
        self.assertEqual(len(node.dependencies), 1)
        self.assertEqual(len(node.include_directories), 1)
        self.assertEqual(node.compile_definitions, ["DEBUG"])
        self.assertEqual(node.compile_options, ["-O2"])
    
    def test_target_node_add_methods(self):
        """Test target node add methods."""
        node = TargetNode(name="mytarget", target_type="executable")
        
        # Test add_source
        source = SourceFileNode("main.cpp")
        node.add_source(source)
        self.assertEqual(len(node.sources), 1)
        self.assertEqual(node.sources[0], source)
        
        # Test add_dependency
        dependency = DependencyNode("mylib")
        node.add_dependency(dependency)
        self.assertEqual(len(node.dependencies), 1)
        self.assertEqual(node.dependencies[0], dependency)
        
        # Test add_include_directory
        include_dir = TargetIncludeDirectoryNode("include")
        node.add_include_directory(include_dir)
        self.assertEqual(len(node.include_directories), 1)
        self.assertEqual(node.include_directories[0], include_dir)
    
    def test_target_node_to_dict(self):
        """Test target node dictionary conversion."""
        sources = [SourceFileNode("main.cpp")]
        dependencies = [DependencyNode("mylib")]
        
        node = TargetNode(
            name="mytarget",
            target_type="executable",
            sources=sources,
            dependencies=dependencies
        )
        
        result = node.to_dict()
        
        self.assertEqual(result['type'], 'target')
        self.assertEqual(result['name'], 'mytarget')
        self.assertEqual(result['target_type'], 'executable')
        self.assertEqual(len(result['sources']), 1)
        self.assertEqual(len(result['dependencies']), 1)


class TestExecutableTargetNode(unittest.TestCase):
    """Test cases for the ExecutableTargetNode class."""
    
    def test_executable_target_node_creation(self):
        """Test executable target node creation."""
        sources = [SourceFileNode("main.cpp")]
        node = ExecutableTargetNode(name="myapp", sources=sources, options="WIN32")
        
        self.assertEqual(node.target_type, "executable")
        self.assertEqual(node.name, "myapp")
        self.assertEqual(node.options, "WIN32")
        self.assertEqual(len(node.sources), 1)
    
    def test_executable_target_node_to_dict(self):
        """Test executable target node dictionary conversion."""
        node = ExecutableTargetNode(name="myapp", options="WIN32")
        result = node.to_dict()
        
        self.assertEqual(result['target_type'], 'executable')
        self.assertEqual(result['name'], 'myapp')
        self.assertEqual(result['options'], 'WIN32')


class TestLibraryTargetNode(unittest.TestCase):
    """Test cases for the LibraryTargetNode class."""
    
    def test_library_target_node_creation(self):
        """Test library target node creation."""
        sources = [SourceFileNode("lib.cpp")]
        node = LibraryTargetNode(
            name="mylib", 
            library_type="SHARED", 
            sources=sources,
            library_specifier="IMPORTED"
        )
        
        self.assertEqual(node.target_type, "library")
        self.assertEqual(node.name, "mylib")
        self.assertEqual(node.library_type, "SHARED")
        self.assertEqual(node.library_specifier, "IMPORTED")
        self.assertEqual(len(node.sources), 1)
    
    def test_library_target_node_defaults(self):
        """Test library target node creation with default values."""
        node = LibraryTargetNode(name="mylib")
        
        self.assertEqual(node.library_type, "STATIC")
        self.assertIsNone(node.library_specifier)
    
    def test_library_target_node_to_dict(self):
        """Test library target node dictionary conversion."""
        node = LibraryTargetNode(name="mylib", library_type="SHARED")
        result = node.to_dict()
        
        self.assertEqual(result['target_type'], 'library')
        self.assertEqual(result['name'], 'mylib')
        self.assertEqual(result['library_type'], 'SHARED')


class TestVariableNode(unittest.TestCase):
    """Test cases for the VariableNode class."""
    
    def test_variable_node_creation(self):
        """Test variable node creation."""
        node = VariableNode(name="MY_VAR", value="test_value", variable_type="string")
        
        self.assertEqual(node.node_type, 'variable')
        self.assertEqual(node.name, "MY_VAR")
        self.assertEqual(node.value, "test_value")
        self.assertEqual(node.variable_type, "string")
    
    def test_variable_node_to_dict(self):
        """Test variable node dictionary conversion."""
        node = VariableNode(name="MY_VAR", value="test_value", variable_type="string")
        result = node.to_dict()
        
        expected = {
            'type': 'variable',
            'name': 'MY_VAR',
            'value': 'test_value',
            'variable_type': 'string'
        }
        self.assertEqual(result, expected)
    
    def test_variable_node_defaults(self):
        """Test variable node creation with default values."""
        node = VariableNode(name="MY_VAR", value="test_value")
        
        self.assertEqual(node.variable_type, "string")


class TestCustomNodes(unittest.TestCase):
    """Test cases for custom command, target, macro, and function nodes."""
    
    def test_custom_command_node(self):
        """Test custom command node creation and conversion."""
        command_data = {'command': 'echo "Hello"', 'args': ['arg1']}
        node = CustomCommandNode(command=command_data)
        
        self.assertEqual(node.node_type, 'custom_command')
        self.assertEqual(node.command, command_data)
        
        result = node.to_dict()
        expected = {
            'type': 'custom_command',
            'command': command_data
        }
        self.assertEqual(result, expected)
    
    def test_custom_target_node(self):
        """Test custom target node creation and conversion."""
        target_data = {'name': 'clean_all', 'command': 'rm -rf build'}
        node = CustomTargetNode(target=target_data)
        
        self.assertEqual(node.node_type, 'custom_target')
        self.assertEqual(node.target, target_data)
        
        result = node.to_dict()
        expected = {
            'type': 'custom_target',
            'target': target_data
        }
        self.assertEqual(result, expected)
    
    def test_custom_macro_node(self):
        """Test custom macro node creation and conversion."""
        macro_data = {'args': ['arg1', 'arg2'], 'body': 'message(${arg1})'}
        node = CustomMacroNode(name="MY_MACRO", data=macro_data)
        
        self.assertEqual(node.node_type, 'custom_macro')
        self.assertEqual(node.name, "MY_MACRO")
        self.assertEqual(node.data, macro_data)
        
        result = node.to_dict()
        expected = {
            'type': 'custom_macro',
            'name': 'MY_MACRO',
            'data': macro_data
        }
        self.assertEqual(result, expected)
    
    def test_custom_function_node(self):
        """Test custom function node creation and conversion."""
        function_data = {'args': ['arg1'], 'body': 'return(${arg1})'}
        node = CustomFunctionNode(name="MY_FUNCTION", data=function_data)
        
        self.assertEqual(node.node_type, 'custom_function')
        self.assertEqual(node.name, "MY_FUNCTION")
        self.assertEqual(node.data, function_data)
        
        result = node.to_dict()
        expected = {
            'type': 'custom_function',
            'name': 'MY_FUNCTION',
            'data': function_data
        }
        self.assertEqual(result, expected)


class TestCMakeAST(unittest.TestCase):
    """Test cases for the CMakeAST class."""
    
    def test_cmake_ast_creation(self):
        """Test CMake AST creation."""
        project = ProjectNode(name="TestProject", minimum_required_version="3.10")
        ast = CMakeAST(project=project, minimum_required_version="3.10")
        
        self.assertEqual(ast.project, project)
        self.assertEqual(ast.minimum_required_version, "3.10")
        self.assertEqual(len(ast.include_directories), 0)
        self.assertEqual(len(ast.targets), 0)
        self.assertEqual(len(ast.variables), 0)
        self.assertEqual(len(ast.custom_commands), 0)
        self.assertEqual(len(ast.custom_targets), 0)
        self.assertEqual(len(ast.custom_macros), 0)
        self.assertEqual(len(ast.custom_functions), 0)
    
    def test_cmake_ast_add_methods(self):
        """Test CMake AST add methods."""
        ast = CMakeAST()
        
        # Test add_include_directory
        include_dir = IncludeDirectoryNode("include")
        ast.add_include_directory(include_dir)
        self.assertEqual(len(ast.include_directories), 1)
        self.assertEqual(ast.include_directories[0], include_dir)
        
        # Test add_target
        target = ExecutableTargetNode("myapp")
        ast.add_target(target)
        self.assertEqual(len(ast.targets), 1)
        self.assertEqual(ast.targets[0], target)
        
        # Test add_variable
        variable = VariableNode("MY_VAR", "value")
        ast.add_variable(variable)
        self.assertEqual(len(ast.variables), 1)
        self.assertEqual(ast.variables[0], variable)
        
        # Test add_custom_command
        command = CustomCommandNode({'command': 'echo test'})
        ast.add_custom_command(command)
        self.assertEqual(len(ast.custom_commands), 1)
        self.assertEqual(ast.custom_commands[0], command)
        
        # Test add_custom_target
        custom_target = CustomTargetNode({'name': 'test'})
        ast.add_custom_target(custom_target)
        self.assertEqual(len(ast.custom_targets), 1)
        self.assertEqual(ast.custom_targets[0], custom_target)
        
        # Test add_custom_macro
        macro = CustomMacroNode("TEST_MACRO", {'body': 'test'})
        ast.add_custom_macro(macro)
        self.assertEqual(len(ast.custom_macros), 1)
        self.assertEqual(ast.custom_macros[0], macro)
        
        # Test add_custom_function
        function = CustomFunctionNode("TEST_FUNCTION", {'body': 'test'})
        ast.add_custom_function(function)
        self.assertEqual(len(ast.custom_functions), 1)
        self.assertEqual(ast.custom_functions[0], function)
    
    def test_cmake_ast_to_dict(self):
        """Test CMake AST dictionary conversion."""
        project = ProjectNode(name="TestProject")
        ast = CMakeAST(project=project, minimum_required_version="3.10")
        
        # Add some components
        ast.add_include_directory(IncludeDirectoryNode("include"))
        ast.add_target(ExecutableTargetNode("myapp"))
        ast.add_variable(VariableNode("MY_VAR", "value"))
        
        result = ast.to_dict()
        
        self.assertIsNotNone(result['project'])
        self.assertEqual(result['minimum_required_version'], "3.10")
        self.assertEqual(len(result['include_directories']), 1)
        self.assertEqual(len(result['targets']), 1)
        self.assertEqual(len(result['variables']), 1)
        self.assertEqual(len(result['custom_commands']), 0)
        self.assertEqual(len(result['custom_targets']), 0)
        self.assertEqual(len(result['custom_macros']), 0)
        self.assertEqual(len(result['custom_functions']), 0)
    
    def test_cmake_ast_empty_to_dict(self):
        """Test CMake AST dictionary conversion when empty."""
        ast = CMakeAST()
        result = ast.to_dict()
        
        self.assertIsNone(result['project'])
        self.assertIsNone(result['minimum_required_version'])
        self.assertEqual(len(result['include_directories']), 0)
        self.assertEqual(len(result['targets']), 0)
        self.assertEqual(len(result['variables']), 0)
        self.assertEqual(len(result['custom_commands']), 0)
        self.assertEqual(len(result['custom_targets']), 0)
        self.assertEqual(len(result['custom_macros']), 0)
        self.assertEqual(len(result['custom_functions']), 0)


if __name__ == '__main__':
    unittest.main()