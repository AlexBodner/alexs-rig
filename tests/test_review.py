#!/usr/bin/env python3
"""Per-file review-mark / review-pending (GitHub Viewed)."""

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

from review_files import mark_files, pending_names  # noqa: E402
from session_base import clear_review_mark, worktree_tree_sha  # noqa: E402


def _git(cwd: Path, *args: str, env: dict | None = None) -> str:
    e = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}  # noqa: E501
    if env:
        e.update(env)
    return subprocess.check_output(["git", "-C", str(cwd), *args], text=True, env=e).strip()


class TestReviewMark(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        os.environ.setdefault("GIT_AUTHOR_NAME", "t")
        os.environ.setdefault("GIT_AUTHOR_EMAIL", "t@t")
        os.environ.setdefault("GIT_COMMITTER_NAME", "t")
        os.environ.setdefault("GIT_COMMITTER_EMAIL", "t@t")
        _git(self.tmp, "init")
        (self.tmp / "keep.py").write_text("a\n", encoding="utf-8")
        (self.tmp / "touch.py").write_text("a\n", encoding="utf-8")
        _git(self.tmp, "add", "-A")
        _git(self.tmp, "commit", "-m", "init")
        sha = _git(self.tmp, "rev-parse", "HEAD")
        (self.tmp / ".alexs-rig").mkdir()
        (self.tmp / ".alexs-rig" / "SESSION_BASE").write_text(sha + "\n", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_pending_before_mark_is_dirty_files(self) -> None:
        (self.tmp / "touch.py").write_text("b\n", encoding="utf-8")
        names = pending_names(self.tmp)
        self.assertEqual(names, ["touch.py"])

    def test_mark_one_file_leaves_the_other(self) -> None:
        (self.tmp / "touch.py").write_text("b\n", encoding="utf-8")
        (self.tmp / "keep.py").write_text("still a\n", encoding="utf-8")
        mark_files(self.tmp, ["touch.py"])
        self.assertEqual(pending_names(self.tmp), ["keep.py"])

    def test_mark_keeps_dot_directory_paths(self) -> None:
        wf = self.tmp / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "ci.yml").write_text("on: push\n", encoding="utf-8")
        self.assertIn(".github/workflows/ci.yml", pending_names(self.tmp))
        mark_files(self.tmp, ["./.github/workflows/ci.yml"])
        self.assertNotIn(".github/workflows/ci.yml", pending_names(self.tmp))

    def test_retouch_unviews_that_file(self) -> None:
        (self.tmp / "touch.py").write_text("b\n", encoding="utf-8")
        (self.tmp / "keep.py").write_text("still a\n", encoding="utf-8")
        mark_files(self.tmp, ["touch.py", "keep.py"])
        self.assertEqual(pending_names(self.tmp), [])
        (self.tmp / "touch.py").write_text("c\n", encoding="utf-8")
        self.assertEqual(pending_names(self.tmp), ["touch.py"])

    def test_clear_review_mark_forgets_file_marks(self) -> None:
        (self.tmp / "touch.py").write_text("b\n", encoding="utf-8")
        mark_files(self.tmp, ["touch.py"])
        self.assertEqual(pending_names(self.tmp), [])
        clear_review_mark(self.tmp)
        self.assertEqual(pending_names(self.tmp), ["touch.py"])

    def test_cli_requires_paths_or_all(self) -> None:
        mark = subprocess.run(
            [sys.executable, str(ROOT / "bin" / "review-mark")],
            cwd=self.tmp,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(mark.returncode, 2, mark.stderr)

    def test_cli_mark_file_and_pending(self) -> None:
        (self.tmp / "touch.py").write_text("b\n", encoding="utf-8")
        (self.tmp / "keep.py").write_text("still a\n", encoding="utf-8")
        mark = subprocess.run(
            [sys.executable, str(ROOT / "bin" / "review-mark"), "touch.py"],
            cwd=self.tmp,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(mark.returncode, 0, mark.stderr)
        self.assertIn("touch.py", mark.stdout)
        pend = subprocess.run(
            [sys.executable, str(ROOT / "bin" / "review-pending"), "--name-only"],
            cwd=self.tmp,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(pend.returncode, 0, pend.stderr)
        self.assertIn("keep.py", pend.stdout)
        self.assertNotIn("touch.py", pend.stdout)
        mark_all = subprocess.run(
            [sys.executable, str(ROOT / "bin" / "review-mark"), "--all"],
            cwd=self.tmp,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(mark_all.returncode, 0, mark_all.stderr)
        pend2 = subprocess.run(
            [sys.executable, str(ROOT / "bin" / "review-pending"), "--name-only"],
            cwd=self.tmp,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(pend2.returncode, 0, pend2.stderr)
        self.assertIn("nothing", pend2.stdout)
        (self.tmp / "touch.py").write_text("c\n", encoding="utf-8")
        pend3 = subprocess.run(
            [sys.executable, str(ROOT / "bin" / "review-pending"), "--name-only"],
            cwd=self.tmp,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(pend3.returncode, 0, pend3.stderr)
        self.assertIn("touch.py", pend3.stdout)
        self.assertNotIn("keep.py", pend3.stdout)

class TestSessionBaseWorktreeSnapshot(unittest.TestCase):
    """SESSION_BASE = worktree snapshot => pre-existing uncommitted work is not
    attributed to the session; only post-session changes are pending."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        os.environ.setdefault("GIT_AUTHOR_NAME", "t")
        os.environ.setdefault("GIT_AUTHOR_EMAIL", "t@t")
        os.environ.setdefault("GIT_COMMITTER_NAME", "t")
        os.environ.setdefault("GIT_COMMITTER_EMAIL", "t@t")
        _git(self.tmp, "init")
        (self.tmp / "keep.py").write_text("a\n", encoding="utf-8")
        _git(self.tmp, "add", "-A")
        _git(self.tmp, "commit", "-m", "init")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _set_session_base(self, sha: str) -> None:
        (self.tmp / ".alexs-rig").mkdir(exist_ok=True)
        (self.tmp / ".alexs-rig" / "SESSION_BASE").write_text(sha + "\n", encoding="utf-8")

    def test_preexisting_uncommitted_work_is_not_pending(self) -> None:
        # Uncommitted work already present when the session opens: a modified
        # tracked file and a brand-new untracked file.
        (self.tmp / "keep.py").write_text("pre-existing edit\n", encoding="utf-8")
        (self.tmp / "pre.py").write_text("pre-existing untracked\n", encoding="utf-8")
        tree = worktree_tree_sha(self.tmp)
        self.assertTrue(tree)
        self._set_session_base(tree)
        # None of the pre-existing work is attributed to the session.
        self.assertEqual(pending_names(self.tmp), [])
        # A new, post-session change *is* pending.
        (self.tmp / "new.py").write_text("agent edit\n", encoding="utf-8")
        self.assertEqual(pending_names(self.tmp), ["new.py"])
