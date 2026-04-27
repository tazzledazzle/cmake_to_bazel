# cmake_to_bazel/e2e_transpile_tests.py
"""End-to-end: CMakeLists.txt -> BUILD matches golden file."""

import io
import os
import pathlib
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock

from cmake_to_bazel.main import main


def _workspace_root() -> pathlib.Path:
    """Workspace root (folder containing testfiles/)."""
    test_srcdir = os.environ.get("TEST_SRCDIR")
    if test_srcdir:
        base = pathlib.Path(test_srcdir)
        for dirpath, dirnames, _ in os.walk(base, topdown=True):
            if "testfiles" in dirnames:
                return pathlib.Path(dirpath).resolve()
    here = pathlib.Path(__file__).resolve()
    for i in range(1, 6):
        p = here.parents[i]
        if (p / "testfiles").is_dir():
            return p
    raise RuntimeError("Could not locate workspace root")


class TestE2ETranspile(unittest.TestCase):
    def test_simple_example_matches_golden(self):
        root = _workspace_root()
        cmake = root / "docs" / "examples" / "simple" / "CMakeLists.txt"
        golden = root / "docs" / "examples" / "simple" / "BUILD.expected"
        self.assertTrue(cmake.is_file(), cmake)
        self.assertTrue(golden.is_file(), golden)

        buf = io.StringIO()
        with mock.patch.object(
            sys,
            "argv",
            ["prog", str(cmake), "/unused", "--dry-run"],
        ):
            with redirect_stdout(buf):
                rc = main(None)
        self.assertEqual(rc, 0)
        self.assertEqual(buf.getvalue(), golden.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
