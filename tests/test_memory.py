#!/usr/bin/env python3
"""Minimal tests for L0 upsert + regen (stdlib unittest)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))

import _memory as mem  # noqa: E402


class TestMemory(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self._old = (mem.ROOT, mem.MEMORY, mem.SNAPSHOTS, mem.ARCHIVE)
        mem.configure_paths(self.tmp)
        mem.ensure_layout()

    def tearDown(self) -> None:
        mem.ROOT, mem.MEMORY, mem.SNAPSHOTS, mem.ARCHIVE = self._old
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_upsert_and_l0(self) -> None:
        mem.upsert_row(mem.MEMORY / "PRINCIPLES.jsonl", {"id": "P-1", "text": "Be brief", "status": "active"})
        mem.upsert_row(
            mem.MEMORY / "PENDING.jsonl",
            {"id": "T-1", "text": "Ship proto", "priority": "P1", "status": "open"},
        )
        out = mem.regen_l0()
        text = out.read_text(encoding="utf-8")
        self.assertIn("[P-1]", text)
        self.assertIn("[T-1]", text)
        self.assertIn("open=1", text)

    def test_archive_principle(self) -> None:
        mem.upsert_row(mem.MEMORY / "PRINCIPLES.jsonl", {"id": "P-1", "text": "old", "status": "active"})
        ok = mem.archive_row(mem.MEMORY / "PRINCIPLES.jsonl", "PRINCIPLES.jsonl", "P-1", reason="test")
        self.assertTrue(ok)
        active = mem.read_jsonl(mem.MEMORY / "PRINCIPLES.jsonl")
        self.assertEqual(active, [])
        arch = mem.read_jsonl(mem.ARCHIVE / "PRINCIPLES.jsonl")
        self.assertEqual(arch[0]["text"], "old")

    def test_redact(self) -> None:
        self.assertIn("[REDACTED]", mem.redact("token=sk-abcdefghijklmnop"))

    def test_configure_paths_memory_dir(self) -> None:
        other = Path(tempfile.mkdtemp())
        try:
            mem.configure_paths(other)
            mem.ensure_layout()
            self.assertEqual(mem.MEMORY, (other / "docs" / "memory").resolve())
            mem.configure_paths(other / "docs" / "memory")
            self.assertEqual(mem.MEMORY, (other / "docs" / "memory").resolve())
        finally:
            shutil.rmtree(other, ignore_errors=True)

    def test_l0_show_cli(self) -> None:
        mem.upsert_row(mem.MEMORY / "PRINCIPLES.jsonl", {"id": "P-x", "text": "show me", "status": "active"})
        mem.regen_l0()
        env = {**os.environ, "ALEXS_RIG_MEMORY": str(self.tmp)}
        proc = subprocess.run(
            [sys.executable, str(ROOT / "bin" / "l0-show"), "--root", str(self.tmp)],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("[P-x]", proc.stdout)

    def test_l0_show_missing(self) -> None:
        empty = Path(tempfile.mkdtemp())
        try:
            proc = subprocess.run(
                [sys.executable, str(ROOT / "bin" / "l0-show"), "--root", str(empty)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 1)
            self.assertIn("missing", proc.stderr.lower())
        finally:
            shutil.rmtree(empty, ignore_errors=True)


class TestMiningApply(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from importlib.machinery import SourceFileLoader

        path = ROOT / "bin" / "mine-corrections"
        cls.mc = SourceFileLoader("mine_corrections", str(path)).load_module()

    def test_skip_other_unless_flag(self) -> None:
        mc = self.mc
        self.assertFalse(mc.should_auto_apply("other", 20, apply_other=False, min_evidence=1))
        self.assertTrue(mc.should_auto_apply("other", 20, apply_other=True, min_evidence=1))
        self.assertTrue(mc.should_auto_apply("review_batch", 1, apply_other=False, min_evidence=1))
        self.assertFalse(mc.should_auto_apply("review_batch", 0, apply_other=False, min_evidence=1))

    def test_already_covered(self) -> None:
        mc = self.mc
        existing = [
            {
                "id": "P-review",
                "text": "Prefer batch review (Desktop +N -M / IDE SCM) over stop-on-every-edit; use Edit automatically after Plan.",
            }
        ]
        self.assertTrue(mc.already_covered(mc.TEMPLATES["review_batch"], existing))
        self.assertFalse(mc.already_covered("Never use tabs in this repo", existing))


class TestGraphStatus(unittest.TestCase):
    def setUp(self) -> None:
        sys.path.insert(0, str(ROOT / "hooks"))
        import graph_status as gs  # noqa: E402

        self.gs = gs
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_missing_graphs(self) -> None:
        st = self.gs.graph_status(self.tmp)
        self.assertFalse(st["understand_anything"])
        self.assertFalse(st["codemap"])
        block = self.gs.graph_context_block(self.tmp)
        self.assertIn("<alexs-rig-graph>", block)
        self.assertIn("understand-anything: NO", block)
        self.assertIn("codemap-py: NO", block)

    def test_detects_understand_and_codemap(self) -> None:
        ua = self.tmp / ".understand-anything"
        ua.mkdir()
        (ua / "knowledge-graph.json").write_text("{}", encoding="utf-8")
        cmap = self.tmp / ".cache" / "codemap"
        cmap.mkdir(parents=True)
        (cmap / "demo.json").write_text("{}", encoding="utf-8")
        st = self.gs.graph_status(self.tmp)
        self.assertTrue(st["understand_anything"])
        self.assertTrue(st["codemap"])
        block = self.gs.graph_context_block(self.tmp)
        self.assertIn("understand-anything: YES", block)
        self.assertIn("codemap-py index: YES", block)

    def test_inject_includes_graph_block(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "hooks" / "inject_l0.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        ctx = payload["hookSpecificOutput"]["additionalContext"]
        self.assertIn("alexs-rig-graph", ctx)
        self.assertIn("alexs-rig-l0", ctx)

    def test_reinject_includes_graph_block(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "hooks" / "reinject_l0.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
            input="{}",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        ctx = payload["hookSpecificOutput"]["additionalContext"]
        self.assertIn("alexs-rig-graph", ctx)
        self.assertIn("alexs-rig-l0", ctx)


class TestHarnessLayout(unittest.TestCase):
    def test_graph_rules_in_sync(self) -> None:
        md = (ROOT / "rules" / "knowledge-graph.md").read_text(encoding="utf-8")
        mdc = (ROOT / "rules" / "knowledge-graph.mdc").read_text(encoding="utf-8")
        self.assertEqual(md, mdc)

    def test_agents_md_present(self) -> None:
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("graph-status", text)
        self.assertIn("unittest", text)
        claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("@AGENTS.md", claude)


if __name__ == "__main__":
    unittest.main()
