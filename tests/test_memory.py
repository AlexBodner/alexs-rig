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


def _load(name: str, rel: str):
    from importlib.machinery import SourceFileLoader

    return SourceFileLoader(name, str(ROOT / rel)).load_module()


class TestCaptureDetector(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cc = _load("capture_correction", "hooks/capture_correction.py")

    def test_captures_no_opener_correction(self) -> None:
        score, signals = self.cc.score_correction("no, don't use recursion here")
        self.assertGreaterEqual(score, self.cc.THRESHOLD)
        self.assertIn("opener:no,", signals)
        self.assertIn("negation", signals)

    def test_silent_on_normal_request(self) -> None:
        score, _ = self.cc.score_correction("please add a function that squares a number")
        self.assertLess(score, self.cc.THRESHOLD)

    def test_pending_adds_weight(self) -> None:
        base, _ = self.cc.score_correction("always run the tests first")
        boosted, signals = self.cc.score_correction("always run the tests first", pending=True)
        self.assertEqual(boosted, base + 1)
        self.assertIn("pending", signals)


class TestCaptureHook(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "docs" / "memory").mkdir(parents=True)
        self.inbox = self.tmp / "docs" / "memory" / "mining" / "corrections-inbox.jsonl"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, prompt: str) -> None:
        payload = json.dumps({"prompt": prompt, "cwd": str(self.tmp)})
        proc = subprocess.run(
            [sys.executable, str(ROOT / "hooks" / "capture_correction.py")],
            input=payload,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "", "capture hook must stay silent")

    def test_appends_on_correction(self) -> None:
        self._run("no, don't commit without asking — token=sk-abcdefghijklmnop")
        rows = mem.read_jsonl(self.inbox)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(set(row), {"ts", "text", "score", "signals", "cwd"})
        self.assertIn("opener:no,", row["signals"])
        self.assertIn("[REDACTED]", row["text"])

    def test_silent_on_normal_request(self) -> None:
        self._run("please add a function that squares a number")
        self.assertFalse(self.inbox.exists() and mem.read_jsonl(self.inbox))


class TestMineCorrectionsInbox(unittest.TestCase):
    def setUp(self) -> None:
        self.mem_root = Path(tempfile.mkdtemp())
        self.cursor = Path(tempfile.mkdtemp())
        tdir = self.cursor / "proj-demo" / "agent-transcripts"
        tdir.mkdir(parents=True)
        rows = [
            {"role": "user", "message": {"content": "no, don't commit without asking me first"}},
            {"role": "user", "message": {"content": "please generate the report for Q3"}},
            {"role": "assistant", "message": {"content": "no, ignore me — I am the assistant"}},
        ]
        (tdir / "chat.jsonl").write_text(
            "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8"
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.mem_root, ignore_errors=True)
        shutil.rmtree(self.cursor, ignore_errors=True)

    def test_writes_inbox_not_principles(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "bin" / "mine-corrections"),
                "--transcripts-root",
                str(self.cursor),
                "--root",
                str(self.mem_root),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        memory = self.mem_root / "docs" / "memory"
        inbox = mem.read_jsonl(memory / "mining" / "corrections-inbox.jsonl")
        self.assertEqual(len(inbox), 1)
        self.assertIn("don't commit", inbox[0]["text"])
        self.assertEqual(inbox[0]["source"], "mine-corrections")
        # No template auto-upsert: principles stay empty.
        self.assertEqual(mem.read_jsonl(memory / "PRINCIPLES.jsonl"), [])


class TestCorrectionsCLI(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self._old = (mem.ROOT, mem.MEMORY, mem.SNAPSHOTS, mem.ARCHIVE)
        mem.configure_paths(self.tmp)
        mem.ensure_layout()
        self.inbox = mem.MEMORY / "mining" / "corrections-inbox.jsonl"
        self.archive = mem.MEMORY / "mining" / "corrections-archive.jsonl"

    def tearDown(self) -> None:
        mem.ROOT, mem.MEMORY, mem.SNAPSHOTS, mem.ARCHIVE = self._old
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(ROOT / "bin" / "corrections"), *args, "--root", str(self.tmp)],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_list_and_flush(self) -> None:
        mem.write_jsonl(self.inbox, [{"ts": "t", "text": "no, stop", "score": 3, "signals": ["opener:no,"]}])
        out = self._cli("list")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("1 correction", out.stdout)

        flush = self._cli("flush")
        self.assertEqual(flush.returncode, 0, flush.stderr)
        self.assertEqual(mem.read_jsonl(self.inbox), [])
        self.assertEqual(len(mem.read_jsonl(self.archive)), 1)


class TestSeededPrinciples(unittest.TestCase):
    def test_eight_principles_present(self) -> None:
        rows = mem.read_jsonl(ROOT / "docs" / "memory" / "PRINCIPLES.jsonl")
        ids = {r.get("id") for r in rows}
        for pid in (
            "P-scope",
            "P-verify",
            "P-confirm",
            "P-branch",
            "P-additive",
            "P-loud",
            "P-honest",
            "P-finish",
        ):
            self.assertIn(pid, ids)


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
