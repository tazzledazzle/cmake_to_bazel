# Supported CMake subset and limitations

This document is the **contract** for what `cmake_to_bazel` tries to do today. Anything not listed here should be assumed **unsupported** unless you extend the parser or post-process generated `BUILD` files.

## What the CLI and emitter do today

- Read a single `CMakeLists.txt` (no `add_subdirectory` graph).
- Emit one `BUILD` file under the given output directory (`OUTPUT_DIR/BUILD`).
- Map a **limited** set of commands to **`cc_library`** and **`cc_binary`** only (no `cc_test`, `genrule`, or `filegroup` emission yet).

## Supported constructs (best effort)

| CMake | Notes |
|-------|--------|
| `cmake_minimum_required(VERSION …)` | Captured on the AST; echoed only indirectly in comments if you extend the emitter. |
| `project(name)` | Project name is parsed. |
| `include_directories(…)` | Global include dirs; merged onto each target’s `includes` in Bazel. |
| `add_executable(name src…)` | Common forms (`SOURCES`, `WIN32`, …) per parser tests. |
| `add_library(name …)` | `STATIC` / default shared/object forms with sources; `IMPORTED` / `ALIAS` libraries are skipped in emission. |
| `target_link_libraries(name …)` | `PRIVATE` / `PUBLIC` / `INTERFACE` and mixed forms as implemented in the parser. |
| `target_include_directories` | Scoped includes merged with globals for emission. |
| `set()` / `${VAR}` substitution | Heuristic variable expansion; not full CMake semantics. |
| `if` / `elseif` / `else` / `endif` | Simplified evaluation for **static** conditions the parser recognizes. |

## Explicitly unsupported or high-risk

| Area | Behavior |
|------|----------|
| `add_subdirectory`, `FetchContent`, `ExternalProject` | Not followed; only the **root** `CMakeLists.txt` is read. |
| Generator expressions (`$<…>`) | Not evaluated; may appear verbatim or confuse the parser. |
| `execute_process`, `file(READ …)`, custom CMake modules | Ignored or partially parsed only if text matches regexes. |
| `target_link_libraries` to **imported** targets, `find_package`, `pkg_check_modules` | Dependencies may be missing or wrong in Bazel. |
| **Correctness vs. real CMake** | The regex parser can diverge from what CMake would configure. For authoritative graphs, use CMake’s **File API** (see [`file_api_spike.py`](../cmake_to_bazel/file_api_spike.py) and `codemodel_reply_to_parser_shape`) or wrap CMake under Bazel. |

## Failure modes (what users see)

- **Parse misses**: Unknown commands are skipped; targets may be incomplete with no warning.
- **Invalid Bazel names**: Rare CMake target names may need manual `tags` / renames after generation.
- **Stale output**: Regenerate after editing `CMakeLists.txt`; consider CI `bazel run` / diff on `BUILD` if you check in generated files.

## Golden tests

The **simple** example under `docs/examples/simple/` is covered end-to-end: `CMakeLists.txt` → dry-run output must match `BUILD.expected` (`//cmake_to_bazel:e2e_transpile_tests`).
