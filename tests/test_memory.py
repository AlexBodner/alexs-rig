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

    def test_redact_masks_values_and_keeps_prose(self) -> None:
        self.assertEqual(mem.redact("token=sk-abcdefghijklmnop"), "token=[REDACTED]")
        # The leak that motivated this: label redacted, value intact. Value must go, label may stay.
        out = mem.redact("export ROBOFLOW_API_KEY=Be8g4FuxLmqPz3SvttC6 and run")
        self.assertNotIn("Be8g4Fux", out)
        self.assertIn("ROBOFLOW_API_KEY=[REDACTED]", out)
        self.assertNotIn("Be8g4Fux", mem.redact("the key is `Be8g4FuxLmqPz3SvttC6`"))  # bare, unlabelled
        self.assertEqual(mem.redact("Authorization: Bearer abc.def-ghi"), "Authorization: [REDACTED]")
        # Ordinary words are not secrets; a correction's text must survive.
        self.assertEqual(mem.redact("the token budget is 1500 tokens"), "the token budget is 1500 tokens")
        self.assertEqual(mem.redact("use the tokenizer, not the secretary"), "use the tokenizer, not the secretary")

    def test_read_jsonl_skips_torn_line(self) -> None:
        p = self.tmp / "torn.jsonl"
        p.write_text('{"id": "a"}\n{"id": "b", "text": "cut off\n{"id": "c"}\n', encoding="utf-8")
        self.assertEqual([r["id"] for r in mem.read_jsonl(p)], ["a", "c"])

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

    def test_configure_paths_global_default(self) -> None:
        home = Path(tempfile.mkdtemp())
        work = Path(tempfile.mkdtemp())  # no docs/memory here
        old_cwd = Path.cwd()
        keys = ("HOME", "ALEXS_RIG_MEMORY", "ALEXS_RIG_ROOT")
        old_env = {k: os.environ.get(k) for k in keys}
        try:
            os.environ["HOME"] = str(home)
            os.environ.pop("ALEXS_RIG_MEMORY", None)
            os.environ.pop("ALEXS_RIG_ROOT", None)
            os.chdir(work)
            mem.configure_paths()
            self.assertEqual(mem.MEMORY, (home / ".alexs-rig" / "memory").resolve())
        finally:
            os.chdir(old_cwd)
            for k, v in old_env.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
            shutil.rmtree(home, ignore_errors=True)
            shutil.rmtree(work, ignore_errors=True)

    def test_configure_paths_walks_up_from_subdir(self) -> None:
        home = Path(tempfile.mkdtemp())
        project = Path(tempfile.mkdtemp())
        (project / "docs" / "memory").mkdir(parents=True)
        subdir = project / "src" / "pkg"
        subdir.mkdir(parents=True)
        old_cwd = Path.cwd()
        keys = ("HOME", "ALEXS_RIG_MEMORY", "ALEXS_RIG_ROOT")
        old_env = {k: os.environ.get(k) for k in keys}
        try:
            os.environ["HOME"] = str(home)
            os.environ.pop("ALEXS_RIG_MEMORY", None)
            os.environ.pop("ALEXS_RIG_ROOT", None)
            os.chdir(subdir)
            mem.configure_paths()
            self.assertEqual(mem.MEMORY, (project / "docs" / "memory").resolve())
        finally:
            os.chdir(old_cwd)
            for k, v in old_env.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
            shutil.rmtree(home, ignore_errors=True)
            shutil.rmtree(project, ignore_errors=True)

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
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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

    def test_find_memory_root_global_fallback(self) -> None:
        home = Path(tempfile.mkdtemp())
        work = Path(tempfile.mkdtemp())  # no in-project docs/memory
        old_home = os.environ.get("HOME")
        try:
            (home / ".alexs-rig" / "memory" / "mining").mkdir(parents=True)
            os.environ["HOME"] = str(home)
            self.assertEqual(self.cc.find_memory_root(work), home / ".alexs-rig" / "memory")
        finally:
            if old_home is None:
                os.environ.pop("HOME", None)
            else:
                os.environ["HOME"] = old_home
            shutil.rmtree(home, ignore_errors=True)
            shutil.rmtree(work, ignore_errors=True)


class TestCaptureContext(unittest.TestCase):
    """A correction is only useful with the turn it reacts to (and the files in play)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.cc = _load("capture_correction", "hooks/capture_correction.py")

    def test_skips_host_injected_text(self) -> None:
        self.assertTrue(self.cc.is_system_text("<task-notification>\n<task-id>a</task-id>"))
        self.assertTrue(self.cc.is_system_text("[Request interrupted by user]"))
        self.assertFalse(self.cc.is_system_text("no, don't do that"))

    def test_excerpt_reads_last_assistant_turn(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        try:
            tr = tmp / "t.jsonl"
            tr.write_text(
                json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "first"}]}})
                + "\n"
                + json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "latest turn"}]}})
                + "\n",
                encoding="utf-8",
            )
            self.assertEqual(self.cc.last_assistant_excerpt(str(tr)), "latest turn")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_excerpt_missing_transcript_is_empty(self) -> None:
        self.assertEqual(self.cc.last_assistant_excerpt(None), "")
        self.assertEqual(self.cc.last_assistant_excerpt("/nope/missing.jsonl"), "")


class TestCaptureHook(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "docs" / "memory").mkdir(parents=True)
        self.inbox = self.tmp / "docs" / "memory" / "mining" / "corrections-inbox.jsonl"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, prompt: str, transcript: bool = True) -> None:
        tr = self.tmp / "t.jsonl"
        if transcript and not tr.exists():
            tr.write_text(
                json.dumps({"type": "assistant",
                            "message": {"content": [{"type": "text", "text": "I did the thing."}]}}) + "\n",
                encoding="utf-8",
            )
        payload = json.dumps({"prompt": prompt, "cwd": str(self.tmp),
                              "transcript_path": str(tr) if transcript else ""})
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
        self.assertEqual(
            set(row),
            {"ts", "text", "score", "signals", "cwd", "assistant_excerpt", "files", "session_id"},
        )
        self.assertIn("opener:no,", row["signals"])
        self.assertIn("[REDACTED]", row["text"])

    def test_captures_normal_reply_too(self) -> None:
        """The inbox is unfiltered on purpose: selection is the flush's job."""
        self._run("please add a function that squares a number")
        self.assertEqual(len(mem.read_jsonl(self.inbox)), 1)

    def test_skips_session_opening_prompt(self) -> None:
        """No preceding agent turn means there is nothing to correct."""
        self._run("start working on the parser", transcript=False)
        self.assertFalse(self.inbox.exists() and mem.read_jsonl(self.inbox))

    def test_skips_giant_paste(self) -> None:
        self._run("no, don't " + "x" * 5000)
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


class TestShippedMemory(unittest.TestCase):
    """The committed docs/memory is the example a new user gets injected until they have their
    own. Every principle id the README, hooks and skills cite has to exist in it."""

    def test_cited_principles_exist(self) -> None:
        import re

        rows = mem.read_jsonl(ROOT / "docs" / "memory" / "PRINCIPLES.jsonl")
        ids = {r.get("id") for r in rows}
        cited: set[str] = set()
        for path in [ROOT / "README.md", *(ROOT / "skills").rglob("SKILL.md"), *(ROOT / "hooks").glob("*.py")]:
            cited |= set(re.findall(r"\bP-[a-z][a-z-]*[a-z]", path.read_text(encoding="utf-8")))
        self.assertEqual(cited - ids, set())

    def test_snapshot_matches_source(self) -> None:
        rows = mem.read_jsonl(ROOT / "docs" / "memory" / "PRINCIPLES.jsonl")
        snap = (ROOT / "docs" / "memory" / "snapshots" / "L0.md").read_text(encoding="utf-8")
        for r in rows:
            self.assertIn(f"[{r['id']}]", snap)
        self.assertNotIn("OVERFLOW", snap)


class TestMemoryCLIs(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _cli(self, name: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "bin" / name), *args, "--root", str(self.tmp)],
            capture_output=True, text=True, check=False,
        )

    def test_principle_upsert_archives_the_previous_text(self) -> None:
        self.assertEqual(self._cli("principle-upsert", "--id", "P-x", "--text", "first").returncode, 0)
        self.assertEqual(self._cli("principle-upsert", "--id", "P-x", "--text", "second").returncode, 0)
        active = mem.read_jsonl(self.tmp / "docs" / "memory" / "PRINCIPLES.jsonl")
        archived = mem.read_jsonl(self.tmp / "docs" / "memory" / "archive" / "PRINCIPLES.jsonl")
        self.assertEqual([r["text"] for r in active], ["second"])
        self.assertEqual([r["text"] for r in archived], ["first"])
        self.assertIn("[P-x] second", (self.tmp / "docs" / "memory" / "snapshots" / "L0.md").read_text())

    def test_shipped_refuses_empty_artifact_then_logs_and_grades(self) -> None:
        env = {**os.environ, "ALEXS_RIG_MEMORY": str(self.tmp)}

        def run(*a: str) -> subprocess.CompletedProcess[str]:
            cmd = [sys.executable, str(ROOT / "bin" / "shipped"), *a]
            return subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)

        self.assertEqual(run("add", "--what", "post").returncode, 2)
        self.assertEqual(run("add", "--what", "post", "--channel", "x", "--artifact", "hello world").returncode, 0)
        self.assertIn("S001", run("list", "--pending").stdout)
        self.assertEqual(run("outcome", "S001", "--good", "--evidence", "3k views").returncode, 0)
        self.assertIn("3k views", run("list", "--good").stdout)
        self.assertNotIn("S001", run("list", "--pending").stdout)


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
            cwd=str(self.tmp),  # never the checkout itself: SessionStart rewrites its review baseline
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        ctx = payload["hookSpecificOutput"]["additionalContext"]
        self.assertIn("alexs-rig-graph", ctx)
        self.assertIn("alexs-rig-l0", ctx)

    def test_reinject_after_compaction_includes_graph_block(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "hooks" / "inject_l0.py")],
            cwd=str(self.tmp),
            capture_output=True,
            text=True,
            check=False,
            input=json.dumps({"source": "compact"}),
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
