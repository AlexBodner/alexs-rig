#!/usr/bin/env python3
"""Deterministic bits of the calibration harness (grading + L0 build) — no agent calls."""

from __future__ import annotations

import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
run = SourceFileLoader("calib_run", str(ROOT / "evals" / "calibrate" / "run.py")).load_module()


class TestCalibrateGrading(unittest.TestCase):
    def test_regex_check(self) -> None:
        t = {"regex": r"def\s+_\w+\s*\("}
        self.assertTrue(run.follows(t, "def _reverse(xs):\n    return xs[::-1]"))
        self.assertFalse(run.follows(t, "def reverse(xs):\n    return xs[::-1]"))

    def test_contains_check(self) -> None:
        t = {"contains": "# rig"}
        self.assertTrue(run.follows(t, "def f(x):  # rig\n    return x"))
        self.assertFalse(run.follows(t, "def f(x):\n    return x"))

    def test_build_l0_carries_rules(self) -> None:
        l0 = run.build_l0(["[R-1] foo", "[R-2] bar"])
        self.assertIn("[R-1] foo", l0)
        self.assertIn("[R-2] bar", l0)
        self.assertIn("PRINCIPLES", l0)


if __name__ == "__main__":
    unittest.main()
