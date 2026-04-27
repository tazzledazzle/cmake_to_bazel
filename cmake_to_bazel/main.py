# cmake_to_bazel/main.py
"""CLI: transpile CMakeLists.txt to a Bazel BUILD file."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional, Set

from cmake_to_bazel.ast_generator import ASTGenerator
from cmake_to_bazel.bazel_emitter import emit_build
from cmake_to_bazel.parsers.cmake_parser import CMakeParser


def _load_config(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        env = os.environ.get("CMAKE_TO_BAZEL_CONFIG")
        if env and os.path.isfile(env):
            path = env
    if not path:
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _apply_config(
    parsed: Dict[str, Any],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """Apply JSON config: excluded_targets, additional_dependencies."""
    excluded: Set[str] = set(config.get("excluded_targets") or [])
    extra_deps: Dict[str, List[str]] = config.get("additional_dependencies") or {}

    targets = []
    for t in parsed.get("targets") or []:
        name = t.get("name")
        if name in excluded:
            continue
        if name in extra_deps:
            deps = t.get("dependencies")
            if isinstance(deps, list):
                merged = list(deps) + list(extra_deps[name])
                t = dict(t)
                t["dependencies"] = merged
            elif isinstance(deps, dict):
                priv = list(deps.get("PRIVATE") or [])
                t = dict(t)
                t["dependencies"] = dict(deps)
                t["dependencies"]["PRIVATE"] = priv + list(extra_deps[name])
        targets.append(t)

    out = dict(parsed)
    out["targets"] = targets
    return out


def _verbose_from_env() -> bool:
    v = os.environ.get("CMAKE_TO_BAZEL_VERBOSE", "").lower()
    return v in ("1", "true", "yes")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m cmake_to_bazel.main",
        description="Transpile CMakeLists.txt to a Bazel BUILD file.",
    )
    parser.add_argument("cmake_file", help="Path to CMakeLists.txt")
    parser.add_argument(
        "output_dir",
        help="Directory where BUILD will be written (as output_dir/BUILD)",
    )
    parser.add_argument("--config", help="JSON configuration file")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose logging (or set CMAKE_TO_BAZEL_VERBOSE=1)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print BUILD to stdout instead of writing files",
    )
    args = parser.parse_args(argv)

    verbose = args.verbose or _verbose_from_env()
    config = _load_config(args.config)

    cmake_parser = CMakeParser()
    parsed = cmake_parser.parse_file(args.cmake_file)
    parsed = _apply_config(parsed, config)

    gen = ASTGenerator()
    ast = gen.generate_ast(parsed)
    build_content = emit_build(ast)

    if verbose:
        print("Project:", parsed.get("project"), file=sys.stderr)
        print("Targets:", [t.get("name") for t in parsed.get("targets") or []], file=sys.stderr)

    if args.dry_run:
        sys.stdout.write(build_content)
        return 0

    os.makedirs(args.output_dir, exist_ok=True)
    out_path = os.path.join(args.output_dir, "BUILD")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(build_content)
    if verbose:
        print(f"Wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
