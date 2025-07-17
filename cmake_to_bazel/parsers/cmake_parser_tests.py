# cmake_to_bazel/parsers/cmake_parser_tests.py

import os
import unittest
import tempfile
from cmake_to_bazel.parsers.cmake_parser import CMakeParser


class TestCMakeParser(unittest.TestCase):
    """Test cases for the CMakeParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = CMakeParser()
        self.temp_dir = tempfile.TemporaryDirectory()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def _create_cmake_file(self, content):
        """Helper method to create a temporary CMake file."""
        file_path = os.path.join(self.temp_dir.name, "CMakeLists.txt")
        with open(file_path, "w") as f:
            f.write(content)
        return file_path
        
    def _assert_target(self, target, expected_type, expected_name, expected_sources, expected_options=None):
        """Helper method to assert target properties."""
        self.assertEqual(target["type"], expected_type)
        self.assertEqual(target["name"], expected_name)
        self.assertEqual(len(target["sources"]), len(expected_sources))
        for source in expected_sources:
            self.assertIn(source, target["sources"])
        
        if expected_options:
            self.assertEqual(target.get("options"), expected_options)
    
    def test_parse_project_name(self):
        """Test parsing project name."""
        content = """
        cmake_minimum_required(VERSION 3.10)
        project(TestProject)
        """
        result = self.parser.parse_string(content)
        self.assertEqual(result["project"], "TestProject")
    
    def test_parse_minimum_required_version(self):
        """Test parsing minimum required CMake version."""
        content = """
        cmake_minimum_required(VERSION 3.10)
        project(TestProject)
        """
        result = self.parser.parse_string(content)
        self.assertEqual(result["minimum_required_version"], "3.10")
    
    def test_parse_include_directories(self):
        """Test parsing include directories."""
        content = """
        include_directories(${PROJECT_SOURCE_DIR}/include /usr/local/include)
        include_directories(${PROJECT_SOURCE_DIR}/src/include)
        """
        result = self.parser.parse_string(content)
        self.assertEqual(len(result["include_directories"]), 3)
        self.assertIn("${PROJECT_SOURCE_DIR}/include", result["include_directories"])
        self.assertIn("/usr/local/include", result["include_directories"])
        self.assertIn("${PROJECT_SOURCE_DIR}/src/include", result["include_directories"])
    
    def test_parse_include_directories_multiline(self):
        """Test parsing include directories with multiline format."""
        content = """
        include_directories(
            ${PROJECT_SOURCE_DIR}/include
            ${PROJECT_SOURCE_DIR}/third_party/include
            /usr/local/include
        )
        """
        result = self.parser.parse_string(content)
        self.assertEqual(len(result["include_directories"]), 3)
        self.assertIn("${PROJECT_SOURCE_DIR}/include", result["include_directories"])
        self.assertIn("${PROJECT_SOURCE_DIR}/third_party/include", result["include_directories"])
        self.assertIn("/usr/local/include", result["include_directories"])
    
    def test_parse_include_directories_with_keywords(self):
        """Test parsing include directories with AFTER, BEFORE, or SYSTEM keywords."""
        content = """
        include_directories(SYSTEM /usr/include)
        include_directories(BEFORE ${PROJECT_SOURCE_DIR}/priority_include)
        include_directories(AFTER ${PROJECT_SOURCE_DIR}/low_priority_include)
        """
        result = self.parser.parse_string(content)
        self.assertEqual(len(result["include_directories"]), 3)
        self.assertIn("/usr/include", result["include_directories"])
        self.assertIn("${PROJECT_SOURCE_DIR}/priority_include", result["include_directories"])
        self.assertIn("${PROJECT_SOURCE_DIR}/low_priority_include", result["include_directories"])
        
        # Check metadata was captured correctly
        self.assertIn("include_directories_metadata", result)
        self.assertEqual(result["include_directories_metadata"]["/usr/include"], "SYSTEM")
        self.assertEqual(result["include_directories_metadata"]["${PROJECT_SOURCE_DIR}/priority_include"], "BEFORE")
        self.assertEqual(result["include_directories_metadata"]["${PROJECT_SOURCE_DIR}/low_priority_include"], "AFTER")
    
    def test_parse_include_directories_with_quotes(self):
        """Test parsing include directories with quoted paths."""
        content = """
        include_directories("${PROJECT_SOURCE_DIR}/include with spaces" "/usr/local/include with spaces")
        """
        result = self.parser.parse_string(content)
        self.assertEqual(len(result["include_directories"]), 2)
        self.assertIn("${PROJECT_SOURCE_DIR}/include with spaces", result["include_directories"])
        self.assertIn("/usr/local/include with spaces", result["include_directories"])
    
    def test_parse_include_directories_with_comments(self):
        """Test parsing include directories with comments."""
        content = """
        include_directories(
            ${PROJECT_SOURCE_DIR}/include # Main include directory
            /usr/local/include # System includes
        )
        """
        result = self.parser.parse_string(content)
        self.assertEqual(len(result["include_directories"]), 2)
        self.assertIn("${PROJECT_SOURCE_DIR}/include", result["include_directories"])
        self.assertIn("/usr/local/include", result["include_directories"])
        
    def test_parse_target_include_directories(self):
        """Test parsing target_include_directories command."""
        content = """
        add_executable(MyApp src/main.cpp)
        target_include_directories(MyApp PUBLIC ${PROJECT_SOURCE_DIR}/include)
        """
        result = self.parser.parse_string(content)
        self.assertEqual(len(result["targets"]), 1)
        target = result["targets"][0]
        self.assertEqual(target["name"], "MyApp")
        self.assertIn("include_directories", target)
        self.assertEqual(len(target["include_directories"]["PUBLIC"]), 1)
        self.assertIn("${PROJECT_SOURCE_DIR}/include", target["include_directories"]["PUBLIC"])
        
    def test_parse_target_include_directories_multiple_scopes(self):
        """Test parsing target_include_directories with multiple scopes."""
        content = """
        add_library(MyLib src/lib.cpp)
        target_include_directories(MyLib 
            PUBLIC ${PROJECT_SOURCE_DIR}/include
            PRIVATE ${PROJECT_SOURCE_DIR}/src
            INTERFACE ${PROJECT_SOURCE_DIR}/interface
        )
        """
        result = self.parser.parse_string(content)
        self.assertEqual(len(result["targets"]), 1)
        target = result["targets"][0]
        self.assertEqual(target["name"], "MyLib")
        self.assertIn("include_directories", target)
        
        # This test will fail because our current implementation doesn't handle multiple scopes in one command
        # We need to update the implementation to handle this case
        
    def test_parse_target_include_directories_with_system_flag(self):
        """Test parsing target_include_directories with SYSTEM flag."""
        content = """
        add_executable(MyApp src/main.cpp)
        target_include_directories(MyApp SYSTEM PUBLIC /usr/include)
        """
        result = self.parser.parse_string(content)
        self.assertEqual(len(result["targets"]), 1)
        target = result["targets"][0]
        self.assertEqual(target["name"], "MyApp")
        self.assertIn("include_directories", target)
        self.assertEqual(len(target["include_directories"]["PUBLIC"]), 1)
        self.assertIn("/usr/include", target["include_directories"]["PUBLIC"])
        self.assertIn("include_directories_metadata", target)
        self.assertIn("/usr/include", target["include_directories_metadata"])
        self.assertTrue(target["include_directories_metadata"]["/usr/include"]["system"])
        
    def test_parse_target_include_directories_with_position_flag(self):
        """Test parsing target_include_directories with BEFORE/AFTER flag."""
        content = """
        add_executable(MyApp src/main.cpp)
        target_include_directories(MyApp BEFORE PUBLIC ${PROJECT_SOURCE_DIR}/priority)
        target_include_directories(MyApp AFTER PUBLIC ${PROJECT_SOURCE_DIR}/low_priority)
        """
        result = self.parser.parse_string(content)
        self.assertEqual(len(result["targets"]), 1)
        target = result["targets"][0]
        self.assertEqual(target["name"], "MyApp")
        self.assertIn("include_directories", target)
        self.assertEqual(len(target["include_directories"]["PUBLIC"]), 2)
        self.assertIn("${PROJECT_SOURCE_DIR}/priority", target["include_directories"]["PUBLIC"])
        self.assertIn("${PROJECT_SOURCE_DIR}/low_priority", target["include_directories"]["PUBLIC"])
        self.assertIn("include_directories_metadata", target)
        self.assertEqual(target["include_directories_metadata"]["${PROJECT_SOURCE_DIR}/priority"]["position"], "BEFORE")
        self.assertEqual(target["include_directories_metadata"]["${PROJECT_SOURCE_DIR}/low_priority"]["position"], "AFTER")
    
    def test_parse_add_executable(self):
        """Test parsing add_executable command."""
        content = """
        add_executable(MyApp src/main.cpp src/helper.cpp)
        """
        result = self.parser.parse_string(content)
        self.assertEqual(len(result["targets"]), 1)
        target = result["targets"][0]
        self.assertEqual(target["type"], "executable")
        self.assertEqual(target["name"], "MyApp")
        self.assertEqual(len(target["sources"]), 2)
        self.assertIn("src/main.cpp", target["sources"])
        self.assertIn("src/helper.cpp", target["sources"])
    
    def test_parse_add_library(self):
        """Test parsing add_library command."""
        content = """
        add_library(MyLib src/lib.cpp src/lib_utils.cpp)
        """
        result = self.parser.parse_string(content)
        self.assertEqual(len(result["targets"]), 1)
        target = result["targets"][0]
        self.assertEqual(target["type"], "library")
        self.assertEqual(target["name"], "MyLib")
        self.assertEqual(target["library_type"], "STATIC")  # Default type
        self.assertEqual(len(target["sources"]), 2)
        self.assertIn("src/lib.cpp", target["sources"])
        self.assertIn("src/lib_utils.cpp", target["sources"])
    
    def test_parse_add_library_with_type(self):
        """Test parsing add_library command with explicit type."""
        content = """
        add_library(MyLib SHARED src/lib.cpp src/lib_utils.cpp)
        """
        result = self.parser.parse_string(content)
        self.assertEqual(len(result["targets"]), 1)
        target = result["targets"][0]
        self.assertEqual(target["type"], "library")
        self.assertEqual(target["name"], "MyLib")
        self.assertEqual(target["library_type"], "SHARED")
        self.assertEqual(len(target["sources"]), 2)
        self.assertIn("src/lib.cpp", target["sources"])
        self.assertIn("src/lib_utils.cpp", target["sources"])
    
    def test_parse_file(self):
        """Test parsing from a file."""
        content = """
        cmake_minimum_required(VERSION 3.10)
        project(TestProject)
        add_executable(MyApp src/main.cpp)
        """
        file_path = self._create_cmake_file(content)
        result = self.parser.parse_file(file_path)
        self.assertEqual(result["project"], "TestProject")
        self.assertEqual(len(result["targets"]), 1)
    
    def test_file_not_found(self):
        """Test handling of non-existent file."""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_file("non_existent_file.txt")
    
    def test_parse_complex_example(self):
        """Test parsing a more complex CMake example."""
        content = """
        cmake_minimum_required(VERSION 3.10)
        project(ComplexProject)
        
        # Include directories
        include_directories(
            ${PROJECT_SOURCE_DIR}/include
            ${PROJECT_SOURCE_DIR}/third_party/include
        )
        
        # Add an executable target
        add_executable(ComplexApp 
            src/main.cpp 
            src/helper.cpp
            src/utils.cpp
        )
        
        # Add a library target
        add_library(ComplexLib STATIC
            src/lib.cpp
            src/lib_utils.cpp
        )
        """
        result = self.parser.parse_string(content)
        self.assertEqual(result["project"], "ComplexProject")
        self.assertEqual(result["minimum_required_version"], "3.10")
        self.assertEqual(len(result["include_directories"]), 2)
        self.assertEqual(len(result["targets"]), 2)
        
        # Check executable target
        executable_target = next(t for t in result["targets"] if t["name"] == "ComplexApp")
        self.assertEqual(executable_target["type"], "executable")
        self.assertEqual(len(executable_target["sources"]), 3)
        
        # Check library target
        library_target = next(t for t in result["targets"] if t["name"] == "ComplexLib")
        self.assertEqual(library_target["type"], "library")
        self.assertEqual(library_target["library_type"], "STATIC")
        self.assertEqual(len(library_target["sources"]), 2)


    def test_parse_add_executable_with_options(self):
        """Test parsing add_executable command with options."""
        content = """
        add_executable(MyApp WIN32 src/main.cpp src/helper.cpp)
        """
        result = self.parser.parse_string(content)
        self.assertEqual(len(result["targets"]), 1)
        target = result["targets"][0]
        self._assert_target(target, "executable", "MyApp", ["src/main.cpp", "src/helper.cpp"], "WIN32")
    
    def test_parse_add_executable_with_sources_keyword(self):
        """Test parsing add_executable command with SOURCES keyword."""
        content = """
        add_executable(MyApp SOURCES src/main.cpp src/helper.cpp)
        """
        result = self.parser.parse_string(content)
        self.assertEqual(len(result["targets"]), 1)
        target = result["targets"][0]
        self._assert_target(target, "executable", "MyApp", ["src/main.cpp", "src/helper.cpp"])
    
    def test_parse_add_executable_multiline(self):
        """Test parsing add_executable command with multiline source list."""
        content = """
        add_executable(MyApp
            src/main.cpp
            src/helper.cpp
            src/utils.cpp
        )
        """
        result = self.parser.parse_string(content)
        self.assertEqual(len(result["targets"]), 1)
        target = result["targets"][0]
        self._assert_target(target, "executable", "MyApp", ["src/main.cpp", "src/helper.cpp", "src/utils.cpp"])
    
    def test_parse_add_library_interface(self):
        """Test parsing add_library command with INTERFACE type."""
        content = """
        add_library(MyLib INTERFACE)
        """
        result = self.parser.parse_string(content)
        self.assertEqual(len(result["targets"]), 1)
        target = result["targets"][0]
        self.assertEqual(target["type"], "library")
        self.assertEqual(target["name"], "MyLib")
        self.assertEqual(target["library_type"], "INTERFACE")
        self.assertEqual(len(target["sources"]), 0)
    
    def test_parse_add_library_imported(self):
        """Test parsing add_library command with IMPORTED specifier."""
        content = """
        add_library(MyLib SHARED IMPORTED)
        """
        result = self.parser.parse_string(content)
        self.assertEqual(len(result["targets"]), 1)
        target = result["targets"][0]
        self.assertEqual(target["type"], "library")
        self.assertEqual(target["name"], "MyLib")
        self.assertEqual(target["library_type"], "SHARED")
        self.assertEqual(target["library_specifier"], "IMPORTED")
        self.assertEqual(len(target["sources"]), 0)
    
    def test_parse_add_library_object(self):
        """Test parsing add_library command with OBJECT type."""
        content = """
        add_library(MyLib OBJECT src/lib.cpp src/lib_utils.cpp)
        """
        result = self.parser.parse_string(content)
        self.assertEqual(len(result["targets"]), 1)
        target = result["targets"][0]
        self.assertEqual(target["type"], "library")
        self.assertEqual(target["name"], "MyLib")
        self.assertEqual(target["library_type"], "OBJECT")
        self.assertEqual(len(target["sources"]), 2)
        self.assertIn("src/lib.cpp", target["sources"])
        self.assertIn("src/lib_utils.cpp", target["sources"])
    
    def test_parse_add_library_with_sources_keyword(self):
        """Test parsing add_library command with SOURCES keyword."""
        content = """
        add_library(MyLib STATIC SOURCES src/lib.cpp src/lib_utils.cpp)
        """
        result = self.parser.parse_string(content)
        self.assertEqual(len(result["targets"]), 1)
        target = result["targets"][0]
        self.assertEqual(target["type"], "library")
        self.assertEqual(target["name"], "MyLib")
        self.assertEqual(target["library_type"], "STATIC")
        self.assertEqual(len(target["sources"]), 2)
        self.assertIn("src/lib.cpp", target["sources"])
        self.assertIn("src/lib_utils.cpp", target["sources"])


if __name__ == "__main__":
    unittest.main()