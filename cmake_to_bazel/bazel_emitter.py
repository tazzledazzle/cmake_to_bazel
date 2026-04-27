# cmake_to_bazel/bazel_emitter.py
"""Emit Bazel BUILD file content from a CMakeAST."""

import json
from typing import TYPE_CHECKING, List, Set

from cmake_to_bazel.ast_nodes import (
    CMakeAST,
    ExecutableTargetNode,
    LibraryTargetNode,
    TargetNode,
)

if TYPE_CHECKING:
    from cmake_to_bazel.ast_nodes import DependencyNode


def _bazel_str_list(paths: List[str], indent: str) -> str:
    if not paths:
        return "[]"
    lines = ["["]
    for p in paths:
        lines.append(f"{indent}    {json.dumps(p)},")
    lines.append(f"{indent}]")
    return "\n".join(lines)


def _norm_path(p: str) -> str:
    if p.startswith("./"):
        return p[2:]
    return p


def _global_include_paths(ast: CMakeAST) -> List[str]:
    return [n.path for n in ast.include_directories]


def _target_include_paths(target: TargetNode) -> List[str]:
    return [inc.path for inc in target.include_directories]


def _merged_includes(ast: CMakeAST, target: TargetNode) -> List[str]:
    seen: Set[str] = set()
    out: List[str] = []
    for p in _global_include_paths(ast) + _target_include_paths(target):
        n = _norm_path(p)
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def _dep_labels(deps: List["DependencyNode"]) -> List[str]:
    return [":" + d.name for d in deps]


def emit_build(ast: CMakeAST) -> str:
    """
    Generate a BUILD file string from a CMake AST.

    Libraries are emitted before executables so link order matches typical CMake usage.
    """
    lines: List[str] = [
        "# Generated from CMakeLists.txt by cmake_to_bazel transpiler",
        "",
    ]

    libs = [t for t in ast.targets if isinstance(t, LibraryTargetNode)]
    exes = [t for t in ast.targets if isinstance(t, ExecutableTargetNode)]
    other = [t for t in ast.targets if not isinstance(t, (LibraryTargetNode, ExecutableTargetNode))]

    def emit_library(t: LibraryTargetNode) -> None:
        if t.library_specifier in ("IMPORTED", "ALIAS"):
            lines.append(f"# Skipped IMPORTED/ALIAS library: {t.name}")
            lines.append("")
            return
        srcs = [s.path for s in t.sources]
        incs = _merged_includes(ast, t)
        lines.append("cc_library(")
        lines.append(f'    name = "{t.name}",')
        if srcs:
            lines.append(f"    srcs = {_bazel_str_list(srcs, '    ')},")
        else:
            lines.append("    srcs = [],")
        if incs:
            lines.append(f"    includes = {_bazel_str_list(incs, '    ')},")
        deps = _dep_labels(t.dependencies)
        if deps:
            lines.append(f"    deps = {_bazel_str_list(deps, '    ')},")
        lines.append(")")
        lines.append("")

    def emit_executable(t: ExecutableTargetNode) -> None:
        srcs = [s.path for s in t.sources]
        incs = _merged_includes(ast, t)
        lines.append("cc_binary(")
        lines.append(f'    name = "{t.name}",')
        lines.append(f"    srcs = {_bazel_str_list(srcs, '    ')},")
        if incs:
            lines.append(f"    includes = {_bazel_str_list(incs, '    ')},")
        deps = _dep_labels(t.dependencies)
        if deps:
            lines.append(f"    deps = {_bazel_str_list(deps, '    ')},")
        lines.append(")")
        lines.append("")

    for t in libs:
        emit_library(t)
    for t in exes:
        emit_executable(t)
    for t in other:
        lines.append(f"# Unhandled target type {t.target_type}: {t.name}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
