#!/usr/bin/env python3
"""bin/verify: run project checks, record non-blocking PASS/FAIL status."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "bin" / "verify"), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )


def _write_verify(root: Path, command: str) -> None:
    (root / ".alexs-rig").mkdir(parents=True, exist_ok=True)
    (root / ".alexs-rig" / "verify").write_text(command + "\n", encoding="utf-8")


class TestVerify(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _status(self) -> dict:
        return json.loads((self.tmp / ".alexs-rig" / "verify-status.json").read_text(encoding="utf-8"))

    def test_custom_pass_command_writes_ok_true(self) -> None:
        _write_verify(self.tmp, "true")
        proc = _run(self.tmp)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("PASS", proc.stdout)
        status = self._status()
        self.assertTrue(status["ok"])
        self.assertEqual(status["returncode"], 0)

    def test_custom_fail_command_writes_ok_false(self) -> None:
        _write_verify(self.tmp, "false")
        proc = _run(self.tmp)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("FAIL", proc.stdout)
        status = self._status()
        self.assertFalse(status["ok"])
        self.assertNotEqual(status["returncode"], 0)

    def test_summary_captures_output_tail(self) -> None:
        _write_verify(self.tmp, "echo hello-from-check")
        proc = _run(self.tmp)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("hello-from-check", self._status()["summary"])

    def test_no_command_found_is_silent_no_crash(self) -> None:
        proc = _run(self.tmp)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("no check command", proc.stdout)
        self.assertFalse((self.tmp / ".alexs-rig" / "verify-status.json").exists())


if __name__ == "__main__":
    unittest.main()
