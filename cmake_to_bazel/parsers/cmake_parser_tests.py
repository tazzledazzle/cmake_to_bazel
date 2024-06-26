# cmake_to_bazel/parsers/cmake_parser_test.py

import unittest
from cmake_parser import parse_cmake


class TestCMakeParser(unittest.TestCase):
    def test_parse_simple_cmake(self):
        cmake_content = """
        cmake_minimum_required(VERSION 3.10)
        project(SimpleProject)
        add_executable(MyApp src/main.cpp src/helper.cpp)
        add_library(MyLib src/lib.cpp)
        target_link_libraries(MyApp MyLib)
        """
        with open('CMakeLists.txt', 'w') as f:
            f.write(cmake_content)
        project = parse_cmake('CMakeLists.txt')
        self.assertEqual(len(project['targets']), 2)


if __name__ == '__main__':
    unittest.main()
