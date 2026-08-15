#!/usr/bin/env python3
"""Incremental codebase-graph staleness tracking (git-based, deterministic)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "hooks"))

import graph_status as gs  # noqa: E402
from session_base import worktree_tree_sha  # noqa: E402


def _git(cwd: Path, *args: str) -> str:
    e = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
    }
    return subprocess.check_output(["git", "-C", str(cwd), *args], text=True, env=e).strip()


class TestGraphStaleness(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        _git(self.tmp, "init")
        (self.tmp / "mod.py").write_text("a = 1\n", encoding="utf-8")
        (self.tmp / "readme.md").write_text("hi\n", encoding="utf-8")
        _git(self.tmp, "add", "-A")
        _git(self.tmp, "commit", "-m", "init")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _mark(self) -> None:
        gs.set_graph_base(self.tmp, worktree_tree_sha(self.tmp))

    def test_no_base_means_no_stale(self) -> None:
        self.assertEqual(gs.stale_source_files(self.tmp), [])

    def test_source_change_is_stale_docs_are_not(self) -> None:
        self._mark()
        self.assertEqual(gs.stale_source_files(self.tmp), [])
        (self.tmp / "mod.py").write_text("a = 2\n", encoding="utf-8")
        (self.tmp / "readme.md").write_text("changed\n", encoding="utf-8")
        (self.tmp / "new.py").write_text("b = 3\n", encoding="utf-8")  # untracked source
        stale = gs.stale_source_files(self.tmp)
        self.assertIn("mod.py", stale)
        self.assertIn("new.py", stale)
        self.assertNotIn("readme.md", stale)

    def test_remark_resets_staleness(self) -> None:
        self._mark()
        (self.tmp / "mod.py").write_text("a = 2\n", encoding="utf-8")
        self.assertTrue(gs.stale_source_files(self.tmp))
        self._mark()
        self.assertEqual(gs.stale_source_files(self.tmp), [])

    def test_context_block_flags_stale_when_graph_exists(self) -> None:
        (self.tmp / ".understand-anything").mkdir()
        (self.tmp / ".understand-anything" / "knowledge-graph.json").write_text("{}", encoding="utf-8")
        self._mark()
        (self.tmp / "mod.py").write_text("a = 9\n", encoding="utf-8")
        block = gs.graph_context_block(self.tmp)
        self.assertIn("STALE: 1 source file", block)

    def test_graph_mark_cli_sets_base(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "bin" / "graph-mark")],
            cwd=self.tmp,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(gs.graph_base_path(self.tmp).is_file())
        self.assertIn("graph-base set", proc.stdout)


class TestGraphSeed(unittest.TestCase):
    """A new worktree starts from main's graph, then only its own edits are stale."""

    def setUp(self) -> None:
        self.main = Path(tempfile.mkdtemp())
        _git(self.main, "init")
        _git(self.main, "branch", "-M", "main")
        (self.main / "app.py").write_text("x = 1\n", encoding="utf-8")
        _git(self.main, "add", "-A")
        _git(self.main, "commit", "-m", "init")
        # main has a built graph + graph-base
        (self.main / ".understand-anything").mkdir()
        (self.main / ".understand-anything" / "knowledge-graph.json").write_text('{"n": 1}', encoding="utf-8")
        gs.set_graph_base(self.main, worktree_tree_sha(self.main))
        (self.main / ".alexs-rig" / "style.md").write_text("# style\nGoogle docstrings.\n", encoding="utf-8")
        # a linked feature worktree (shares the object store with main)
        self.wt = Path(tempfile.mkdtemp()) / "feat"
        _git(self.main, "worktree", "add", "-b", "feat", str(self.wt))

    def tearDown(self) -> None:
        subprocess.run(
            ["git", "-C", str(self.main), "worktree", "remove", "--force", str(self.wt)],
            capture_output=True, check=False,
        )
        shutil.rmtree(self.main, ignore_errors=True)
        shutil.rmtree(self.wt.parent, ignore_errors=True)

    def test_seed_auto_detects_main_and_isolates_edits(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "bin" / "graph-seed")],
            cwd=str(self.wt), capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        # graph + graph-base copied from main
        self.assertTrue((self.wt / ".understand-anything" / "knowledge-graph.json").is_file())
        self.assertTrue((self.wt / ".alexs-rig" / "style.md").is_file())  # style note carried too
        self.assertEqual(gs.graph_base_sha(self.wt), gs.graph_base_sha(self.main))
        # fresh feature worktree (branched from main, no edits) → nothing stale
        self.assertEqual(gs.stale_source_files(self.wt), [])
        # an edit here becomes the only stale file — grows from main's baseline
        (self.wt / "app.py").write_text("x = 2\n", encoding="utf-8")
        self.assertEqual(gs.stale_source_files(self.wt), ["app.py"])

    def test_seed_refuses_to_overwrite_existing_graph(self) -> None:
        # the worktree already has its own (locally updated) graph
        (self.wt / ".understand-anything").mkdir()
        local_graph = self.wt / ".understand-anything" / "knowledge-graph.json"
        local_graph.write_text('{"n": 999}', encoding="utf-8")

        proc = subprocess.run(
            [sys.executable, str(ROOT / "bin" / "graph-seed")],
            cwd=str(self.wt), capture_output=True, text=True, check=False,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(local_graph.read_text(encoding="utf-8"), '{"n": 999}')

        proc = subprocess.run(
            [sys.executable, str(ROOT / "bin" / "graph-seed"), "--force"],
            cwd=str(self.wt), capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(local_graph.read_text(encoding="utf-8"), '{"n": 1}')


class TestGraphStaleTruncation(unittest.TestCase):
    """STALE count must be honest when the file list is capped."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        _git(self.tmp, "init")
        (self.tmp / "mod.py").write_text("a = 1\n", encoding="utf-8")
        _git(self.tmp, "add", "-A")
        _git(self.tmp, "commit", "-m", "init")
        (self.tmp / ".understand-anything").mkdir()
        (self.tmp / ".understand-anything" / "knowledge-graph.json").write_text("{}", encoding="utf-8")
        gs.set_graph_base(self.tmp, worktree_tree_sha(self.tmp))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_block_shows_truncated_count_when_over_cap(self) -> None:
        for i in range(60):
            (self.tmp / f"f{i}.py").write_text(f"x = {i}\n", encoding="utf-8")
        self.assertEqual(len(gs.stale_source_files(self.tmp)), 50)  # still capped
        block = gs.graph_context_block(self.tmp)
        self.assertIn("STALE: 50+ source file(s)", block)


if __name__ == "__main__":
    unittest.main()
