# cmake_to_bazel/parsers/cmake_parser.py

import sys
import os


def parse_cmake(file_path):
    # Placeholder parsing logic, extend as needed
    targets = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('add_library') or line.startswith('add_executable'):
                parts = line.split()
                targets.append({
                    'name': parts[1],
                    'sources': parts[2:]
                })
    return targets


def generate_bazel_build(targets, output_dir):
    for target in targets:
        build_content = 'cc_library(\n'
        build_content += f'    name = "{target["name"]}",\n'
        build_content += '    srcs = [\n'
        for src in target['sources']:
            build_content += f'        "{src}",\n'
        build_content += '    ],\n'
        build_content += ')\n'
        output_path = os.path.join(output_dir, target['name'], 'BUILD')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as build_file:
            build_file.write(build_content)


def main():
    cmake_file = sys.argv[1]
    output_dir = sys.argv[2]
    targets = parse_cmake(cmake_file)
    generate_bazel_build(targets, output_dir)


if __name__ == '__main__':
    main()
