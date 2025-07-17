# cmake_to_bazel/ast_generator_tests.py

import unittest
from ast_generator import ASTGenerator


class TestASTGenerator(unittest.TestCase):
    """Test cases for the ASTGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.ast_generator = ASTGenerator()
    
    def test_generate_ast_with_empty_content(self):
        """Test AST generation with empty parsed content."""
        from ast_nodes import CMakeAST
        
        parsed_content = {}
        ast = self.ast_generator.generate_ast(parsed_content)
        
        # Verify basic structure
        self.assertIsInstance(ast, CMakeAST)
        
        # Verify empty content results
        self.assertIsNone(ast.project)
        self.assertIsNone(ast.minimum_required_version)
        self.assertEqual(len(ast.include_directories), 0)
        self.assertEqual(len(ast.targets), 0)
        self.assertEqual(len(ast.variables), 0)
        self.assertEqual(len(ast.custom_commands), 0)
        self.assertEqual(len(ast.custom_targets), 0)
        self.assertEqual(len(ast.custom_macros), 0)
        self.assertEqual(len(ast.custom_functions), 0)
    
    def test_generate_ast_with_invalid_input(self):
        """Test AST generation with invalid input."""
        with self.assertRaises(ValueError):
            self.ast_generator.generate_ast("invalid_input")
        
        with self.assertRaises(ValueError):
            self.ast_generator.generate_ast(None)
    
    def test_create_project_node(self):
        """Test project node creation."""
        parsed_content = {
            'project': 'MyProject',
            'minimum_required_version': '3.10'
        }
        
        ast = self.ast_generator.generate_ast(parsed_content)
        project_node = ast.project
        
        self.assertIsNotNone(project_node)
        self.assertEqual(project_node.node_type, 'project')
        self.assertEqual(project_node.name, 'MyProject')
        self.assertEqual(project_node.minimum_required_version, '3.10')
    
    def test_create_project_node_without_project(self):
        """Test project node creation when no project is defined."""
        parsed_content = {}
        
        ast = self.ast_generator.generate_ast(parsed_content)
        project_node = ast.project
        
        self.assertIsNone(project_node)
    
    def test_create_include_directories_nodes(self):
        """Test include directory nodes creation."""
        parsed_content = {
            'include_directories': ['include', 'src/include'],
            'include_directories_metadata': {
                'include': 'SYSTEM'
            }
        }
        
        ast = self.ast_generator.generate_ast(parsed_content)
        include_nodes = ast.include_directories
        
        self.assertEqual(len(include_nodes), 2)
        
        # Check first include directory
        self.assertEqual(include_nodes[0].node_type, 'include_directory')
        self.assertEqual(include_nodes[0].path, 'include')
        self.assertEqual(include_nodes[0].metadata, 'SYSTEM')
        
        # Check second include directory
        self.assertEqual(include_nodes[1].node_type, 'include_directory')
        self.assertEqual(include_nodes[1].path, 'src/include')
        self.assertEqual(include_nodes[1].metadata, {})
    
    def test_create_executable_target_node(self):
        """Test executable target node creation."""
        parsed_content = {
            'targets': [
                {
                    'type': 'executable',
                    'name': 'my_app',
                    'sources': ['main.cpp', 'app.cpp'],
                    'dependencies': ['lib1', 'lib2'],
                    'options': 'WIN32'
                }
            ]
        }
        
        ast = self.ast_generator.generate_ast(parsed_content)
        target_nodes = ast.targets
        
        self.assertEqual(len(target_nodes), 1)
        
        target = target_nodes[0]
        self.assertEqual(target.node_type, 'target')
        self.assertEqual(target.target_type, 'executable')
        self.assertEqual(target.name, 'my_app')
        self.assertEqual(target.options, 'WIN32')
        
        # Check sources
        sources = target.sources
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0].node_type, 'source_file')
        self.assertEqual(sources[0].path, 'main.cpp')
        self.assertEqual(sources[1].node_type, 'source_file')
        self.assertEqual(sources[1].path, 'app.cpp')
        
        # Check dependencies (legacy format)
        dependencies = target.dependencies
        self.assertEqual(len(dependencies), 2)
        self.assertEqual(dependencies[0].node_type, 'dependency')
        self.assertEqual(dependencies[0].name, 'lib1')
        self.assertEqual(dependencies[0].scope, 'PRIVATE')
        self.assertEqual(dependencies[1].node_type, 'dependency')
        self.assertEqual(dependencies[1].name, 'lib2')
        self.assertEqual(dependencies[1].scope, 'PRIVATE')
    
    def test_create_library_target_node(self):
        """Test library target node creation."""
        parsed_content = {
            'targets': [
                {
                    'type': 'library',
                    'name': 'my_lib',
                    'library_type': 'SHARED',
                    'library_specifier': 'IMPORTED',
                    'sources': ['lib.cpp', 'lib_utils.cpp'],
                    'dependencies': {
                        'PUBLIC': ['public_dep'],
                        'PRIVATE': ['private_dep'],
                        'INTERFACE': ['interface_dep']
                    }
                }
            ]
        }
        
        ast = self.ast_generator.generate_ast(parsed_content)
        target_nodes = ast.targets
        
        self.assertEqual(len(target_nodes), 1)
        
        target = target_nodes[0]
        self.assertEqual(target.node_type, 'target')
        self.assertEqual(target.target_type, 'library')
        self.assertEqual(target.name, 'my_lib')
        self.assertEqual(target.library_type, 'SHARED')
        self.assertEqual(target.library_specifier, 'IMPORTED')
        
        # Check sources
        sources = target.sources
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0].node_type, 'source_file')
        self.assertEqual(sources[0].path, 'lib.cpp')
        
        # Check scoped dependencies
        dependencies = target.dependencies
        self.assertEqual(len(dependencies), 3)
        
        # Find dependencies by scope
        public_deps = [d for d in dependencies if d.scope == 'PUBLIC']
        private_deps = [d for d in dependencies if d.scope == 'PRIVATE']
        interface_deps = [d for d in dependencies if d.scope == 'INTERFACE']
        
        self.assertEqual(len(public_deps), 1)
        self.assertEqual(public_deps[0].name, 'public_dep')
        
        self.assertEqual(len(private_deps), 1)
        self.assertEqual(private_deps[0].name, 'private_dep')
        
        self.assertEqual(len(interface_deps), 1)
        self.assertEqual(interface_deps[0].name, 'interface_dep')
    
    def test_create_target_include_directory_nodes(self):
        """Test target-specific include directory nodes creation."""
        parsed_content = {
            'targets': [
                {
                    'type': 'library',
                    'name': 'my_lib',
                    'sources': ['lib.cpp'],
                    'include_directories': {
                        'PUBLIC': ['public_include'],
                        'PRIVATE': ['private_include'],
                        'INTERFACE': ['interface_include']
                    },
                    'include_directories_metadata': {
                        'public_include': {'system': True, 'position': 'BEFORE'}
                    }
                }
            ]
        }
        
        ast = self.ast_generator.generate_ast(parsed_content)
        target = ast.targets[0]
        include_dirs = target.include_directories
        
        self.assertEqual(len(include_dirs), 3)
        
        # Find include directories by scope
        public_includes = [d for d in include_dirs if d.scope == 'PUBLIC']
        private_includes = [d for d in include_dirs if d.scope == 'PRIVATE']
        interface_includes = [d for d in include_dirs if d.scope == 'INTERFACE']
        
        self.assertEqual(len(public_includes), 1)
        self.assertEqual(public_includes[0].path, 'public_include')
        self.assertEqual(public_includes[0].metadata, {'system': True, 'position': 'BEFORE'})
        
        self.assertEqual(len(private_includes), 1)
        self.assertEqual(private_includes[0].path, 'private_include')
        
        self.assertEqual(len(interface_includes), 1)
        self.assertEqual(interface_includes[0].path, 'interface_include')
    
    def test_create_variable_nodes(self):
        """Test variable nodes creation."""
        parsed_content = {
            'variables': {
                'MY_VAR': 'value1',
                'ANOTHER_VAR': 'value2',
                'EMPTY_VAR': ''
            }
        }
        
        ast = self.ast_generator.generate_ast(parsed_content)
        variable_nodes = ast.variables
        
        self.assertEqual(len(variable_nodes), 3)
        
        # Check variables
        var_dict = {var.name: var.value for var in variable_nodes}
        self.assertEqual(var_dict['MY_VAR'], 'value1')
        self.assertEqual(var_dict['ANOTHER_VAR'], 'value2')
        self.assertEqual(var_dict['EMPTY_VAR'], '')
        
        # Check node structure
        for var in variable_nodes:
            self.assertEqual(var.node_type, 'variable')
            self.assertIsNotNone(var.name)
            self.assertIsNotNone(var.value)
    
    def test_create_custom_command_nodes(self):
        """Test custom command nodes creation."""
        parsed_content = {
            'custom_commands': [
                {'command': 'echo "Hello"'},
                {'command': 'mkdir build'}
            ]
        }
        
        ast = self.ast_generator.generate_ast(parsed_content)
        command_nodes = ast.custom_commands
        
        self.assertEqual(len(command_nodes), 2)
        
        self.assertEqual(command_nodes[0].node_type, 'custom_command')
        self.assertEqual(command_nodes[0].command, {'command': 'echo "Hello"'})
        
        self.assertEqual(command_nodes[1].node_type, 'custom_command')
        self.assertEqual(command_nodes[1].command, {'command': 'mkdir build'})
    
    def test_create_custom_target_nodes(self):
        """Test custom target nodes creation."""
        parsed_content = {
            'custom_targets': [
                {'name': 'clean_all', 'command': 'rm -rf build'},
                {'name': 'docs', 'command': 'doxygen'}
            ]
        }
        
        ast = self.ast_generator.generate_ast(parsed_content)
        target_nodes = ast.custom_targets
        
        self.assertEqual(len(target_nodes), 2)
        
        self.assertEqual(target_nodes[0].node_type, 'custom_target')
        self.assertEqual(target_nodes[0].target, {'name': 'clean_all', 'command': 'rm -rf build'})
        
        self.assertEqual(target_nodes[1].node_type, 'custom_target')
        self.assertEqual(target_nodes[1].target, {'name': 'docs', 'command': 'doxygen'})
    
    def test_create_custom_macro_nodes(self):
        """Test custom macro nodes creation."""
        parsed_content = {
            'custom_macros': {
                'MY_MACRO': {'args': ['arg1', 'arg2'], 'body': 'message(${arg1})'},
                'ANOTHER_MACRO': {'args': [], 'body': 'set(VAR value)'}
            }
        }
        
        ast = self.ast_generator.generate_ast(parsed_content)
        macro_nodes = ast.custom_macros
        
        self.assertEqual(len(macro_nodes), 2)
        
        # Check macro nodes
        macro_dict = {macro.name: macro.data for macro in macro_nodes}
        self.assertEqual(macro_dict['MY_MACRO'], {'args': ['arg1', 'arg2'], 'body': 'message(${arg1})'})
        self.assertEqual(macro_dict['ANOTHER_MACRO'], {'args': [], 'body': 'set(VAR value)'})
        
        # Check node structure
        for macro in macro_nodes:
            self.assertEqual(macro.node_type, 'custom_macro')
            self.assertIsNotNone(macro.name)
            self.assertIsNotNone(macro.data)
    
    def test_create_custom_function_nodes(self):
        """Test custom function nodes creation."""
        parsed_content = {
            'custom_functions': {
                'MY_FUNCTION': {'args': ['arg1'], 'body': 'return(${arg1})'},
                'UTIL_FUNCTION': {'args': ['input', 'output'], 'body': 'set(${output} ${input})'}
            }
        }
        
        ast = self.ast_generator.generate_ast(parsed_content)
        function_nodes = ast.custom_functions
        
        self.assertEqual(len(function_nodes), 2)
        
        # Check function nodes
        function_dict = {func.name: func.data for func in function_nodes}
        self.assertEqual(function_dict['MY_FUNCTION'], {'args': ['arg1'], 'body': 'return(${arg1})'})
        self.assertEqual(function_dict['UTIL_FUNCTION'], {'args': ['input', 'output'], 'body': 'set(${output} ${input})'})
        
        # Check node structure
        for func in function_nodes:
            self.assertEqual(func.node_type, 'custom_function')
            self.assertIsNotNone(func.name)
            self.assertIsNotNone(func.data)
    
    def test_comprehensive_ast_generation(self):
        """Test comprehensive AST generation with all components."""
        parsed_content = {
            'project': 'TestProject',
            'minimum_required_version': '3.15',
            'include_directories': ['include'],
            'targets': [
                {
                    'type': 'executable',
                    'name': 'test_app',
                    'sources': ['main.cpp'],
                    'dependencies': ['test_lib']
                },
                {
                    'type': 'library',
                    'name': 'test_lib',
                    'library_type': 'STATIC',
                    'sources': ['lib.cpp'],
                    'dependencies': {
                        'PUBLIC': ['external_lib']
                    }
                }
            ],
            'variables': {
                'TEST_VAR': 'test_value'
            },
            'custom_commands': [
                {'command': 'echo test'}
            ],
            'custom_targets': [
                {'name': 'test_target', 'command': 'echo target'}
            ],
            'custom_macros': {
                'TEST_MACRO': {'args': [], 'body': 'message(test)'}
            },
            'custom_functions': {
                'TEST_FUNCTION': {'args': ['arg'], 'body': 'return(${arg})'}
            }
        }
        
        ast = self.ast_generator.generate_ast(parsed_content)
        
        # Verify all components are present and correctly structured
        self.assertIsNotNone(ast.project)
        self.assertEqual(ast.project.name, 'TestProject')
        self.assertEqual(ast.minimum_required_version, '3.15')
        self.assertEqual(len(ast.include_directories), 1)
        self.assertEqual(len(ast.targets), 2)
        self.assertEqual(len(ast.variables), 1)
        self.assertEqual(len(ast.custom_commands), 1)
        self.assertEqual(len(ast.custom_targets), 1)
        self.assertEqual(len(ast.custom_macros), 1)
        self.assertEqual(len(ast.custom_functions), 1)


if __name__ == '__main__':
    unittest.main()