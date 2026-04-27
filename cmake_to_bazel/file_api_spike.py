# cmake_to_bazel/file_api_spike.py
"""
Spike: map CMake File API codemodel JSON to the same dict shape as CMakeParser.

Use this to compare fidelity between "regex parse CMakeLists" and "CMake-resolved graph".
See docs/supported_subset.md. Requires a configured build directory with File API replies.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _codemodel_json_from_index(reply_dir: Path) -> Optional[Path]:
    for index in sorted(reply_dir.glob("index-*.json")):
        data = _read_json(index)
        for obj in data.get("objects") or []:
            if obj.get("kind") == "codemodel":
                jf = obj.get("jsonFile")
                if jf:
                    return reply_dir / jf
    return None


def _cmake_type_to_parser(t: str) -> Tuple[str, Optional[str]]:
    if t == "EXECUTABLE":
        return "executable", None
    if t in ("STATIC_LIBRARY", "SHARED_LIBRARY", "MODULE_LIBRARY"):
        return "library", t.replace("_LIBRARY", "")
    if t == "OBJECT_LIBRARY":
        return "library", "OBJECT"
    if t == "INTERFACE_LIBRARY":
        return "library", "INTERFACE"
    return "unknown", None


def _link_dependency_names(target: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    link = target.get("link") or {}
    for lib in link.get("libraries") or []:
        if isinstance(lib, dict) and "target" in lib:
            tid = (lib.get("target") or {}).get("id")
            if tid:
                out.append(tid)
        elif isinstance(lib, dict) and lib.get("fragment"):
            frag = lib["fragment"]
            if frag and not frag.startswith("$"):
                out.append(frag)
    return out


def _resolve_target_ids_to_names(
    targets_by_id: Dict[str, Dict[str, Any]],
    ids: List[str],
) -> List[str]:
    names: List[str] = []
    for i in ids:
        t = targets_by_id.get(i)
        if t and t.get("name"):
            names.append(t["name"])
        else:
            names.append(i)
    return names


def codemodel_reply_to_parser_shape(reply_dir: Path) -> Dict[str, Any]:
    """
    Load codemodel + target JSON files from a File API ``reply`` directory.

    Returns a dict compatible with :meth:`cmake_to_bazel.ast_generator.ASTGenerator.generate_ast`.
    """
    cm_path = _codemodel_json_from_index(reply_dir)
    if not cm_path or not cm_path.is_file():
        raise FileNotFoundError(f"No codemodel index in {reply_dir}")

    codemodel = _read_json(cm_path)
    configs = codemodel.get("configurations") or []
    if not configs:
        return {
            "project": None,
            "minimum_required_version": None,
            "include_directories": [],
            "targets": [],
        }
    cfg0 = configs[0]
    target_entries = cfg0.get("targets") or []

    targets_by_id: Dict[str, Dict[str, Any]] = {}
    raw_targets: List[Dict[str, Any]] = []

    for entry in target_entries:
        jf = entry.get("jsonFile")
        name = entry.get("name")
        tid = entry.get("id")
        if not jf:
            continue
        tpath = reply_dir / jf
        if not tpath.is_file():
            continue
        tdata = _read_json(tpath)
        if tid:
            targets_by_id[tid] = tdata
        raw_targets.append(tdata)

    parser_targets: List[Dict[str, Any]] = []
    for t in raw_targets:
        name = t.get("name")
        ctype = t.get("type") or ""
        ptype, lib_type = _cmake_type_to_parser(ctype)
        if ptype == "unknown":
            continue
        sources = []
        for s in t.get("sources") or []:
            if isinstance(s, dict) and s.get("path"):
                sources.append(s["path"])
        deps_ids = _link_dependency_names(t)
        deps_names = _resolve_target_ids_to_names(targets_by_id, deps_ids)
        if not deps_names:
            deps_names = [d for d in deps_ids if not d.endswith("-id")]

        entry: Dict[str, Any] = {
            "name": name,
            "type": ptype,
            "sources": sources,
            "dependencies": deps_names,
        }
        if lib_type:
            entry["library_type"] = lib_type
        parser_targets.append(entry)

    return {
        "project": None,
        "minimum_required_version": None,
        "include_directories": [],
        "targets": parser_targets,
    }


def prepare_file_api_query(build_dir: Path) -> None:
    """Create the File API query file so the next CMake configure writes codemodel replies."""
    query = build_dir / ".cmake" / "api" / "v1" / "query" / "codemodel-v2"
    query.parent.mkdir(parents=True, exist_ok=True)
    query.write_text("{}", encoding="utf-8")


def run_cmake_configure(source_dir: Path, build_dir: Path) -> None:
    """Run ``cmake -S source -B build`` (requires ``cmake`` on PATH)."""
    build_dir.mkdir(parents=True, exist_ok=True)
    prepare_file_api_query(build_dir)
    subprocess.run(
        ["cmake", "-S", str(source_dir), "-B", str(build_dir)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def compare_parser_vs_file_api(cmake_path: Path, reply_dir: Path) -> Dict[str, Any]:
    """
    Parse ``cmake_path`` with CMakeParser and compare target names/sources to File API shape.

    Returns a small report dict with keys ``parser_only``, ``file_api_only``, ``targets``.
    """
    from cmake_to_bazel.parsers.cmake_parser import CMakeParser

    parser = CMakeParser()
    parsed = parser.parse_file(str(cmake_path))
    api_shape = codemodel_reply_to_parser_shape(reply_dir)

    def key(t: Dict[str, Any]) -> str:
        return t.get("name") or ""

    p_targets = {key(t): t for t in parsed.get("targets") or []}
    a_targets = {key(t): t for t in api_shape.get("targets") or []}

    p_names = set(p_targets)
    a_names = set(a_targets)
    detail = []
    for n in sorted(p_names & a_names):
        ps = tuple(p_targets[n].get("sources") or [])
        al = tuple(a_targets[n].get("sources") or [])
        if ps != al:
            detail.append({"name": n, "parser_sources": ps, "file_api_sources": al})

    return {
        "parser_only": sorted(p_names - a_names),
        "file_api_only": sorted(a_names - p_names),
        "source_mismatches": detail,
    }
