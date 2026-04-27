# cmake_to_bazel/file_api_spike_tests.py
"""Tests for File API codemodel → parser-shaped dict (spike)."""

import pathlib
import unittest

from cmake_to_bazel.file_api_spike import codemodel_reply_to_parser_shape


class TestFileApiSpike(unittest.TestCase):
    def test_minimal_codemodel_fixture(self):
        reply = (
            pathlib.Path(__file__).resolve().parent
            / "testdata"
            / "file_api_minimal"
            / "reply"
        )
        shape = codemodel_reply_to_parser_shape(reply)
        names = {t["name"] for t in shape["targets"]}
        self.assertEqual(names, {"MyApp", "MyLib"})
        by_name = {t["name"]: t for t in shape["targets"]}
        self.assertEqual(by_name["MyLib"]["sources"], ["src/lib.cpp"])
        self.assertEqual(
            by_name["MyApp"]["sources"],
            ["src/main.cpp", "src/helper.cpp"],
        )
        self.assertEqual(by_name["MyApp"]["dependencies"], ["MyLib"])


if __name__ == "__main__":
    unittest.main()
