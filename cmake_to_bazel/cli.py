"""Bazel py_binary entrypoint (runs cmake_to_bazel.main)."""

import sys

from cmake_to_bazel.main import main

if __name__ == "__main__":
    raise SystemExit(main())
