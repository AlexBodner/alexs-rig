#!/usr/bin/env python3
"""Per-file review-mark / review-pending (GitHub Viewed)."""

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
sys.path.insert(0, str(ROOT / "hooks"))

from review_files import mark_files, pending_names  # noqa: E402
from session_base import clear_review_mark  # noqa: E402


def _git(cwd: Path, *args: str, env: dict | None = None) -> str:
    e = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
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

    def test_node_store_matches_python(self) -> None:
        if not shutil.which("node"):
            self.skipTest("node")
        js = ROOT / "extensions" / "alexs-rig-review" / "store.js"
        (self.tmp / "touch.py").write_text("b\n", encoding="utf-8")
        (self.tmp / "keep.py").write_text("still a\n", encoding="utf-8")
        proc = subprocess.run(
            ["node", str(js), "mark", str(self.tmp), "touch.py"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertEqual(pending_names(self.tmp), ["keep.py"])
        proc2 = subprocess.run(
            ["node", str(js), "pending", str(self.tmp)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc2.returncode, 0, proc2.stderr)
        self.assertEqual(proc2.stdout.strip(), "keep.py")
        (self.tmp / "touch.py").write_text("c\n", encoding="utf-8")
        proc3 = subprocess.run(
            ["node", str(js), "pending", str(self.tmp)],
            capture_output=True,
            text=True,
            check=False,
        )
        names = {n for n in proc3.stdout.splitlines() if n.strip()}
        self.assertEqual(names, {"touch.py", "keep.py"})

    def test_pr_compare_includes_committed_and_session(self) -> None:
        if not shutil.which("node"):
            self.skipTest("node")
        js = ROOT / "extensions" / "alexs-rig-review" / "store.js"
        base = _git(self.tmp, "rev-parse", "HEAD")
        home = _git(self.tmp, "branch", "--show-current") or "master"
        _git(self.tmp, "checkout", "-b", "feat")
        (self.tmp / "extra.py").write_text("x\n", encoding="utf-8")
        _git(self.tmp, "add", "extra.py")
        _git(self.tmp, "commit", "-m", "pr file")
        head = _git(self.tmp, "rev-parse", "HEAD")
        (self.tmp / ".alexs-rig" / "SESSION_BASE").write_text(head + "\n", encoding="utf-8")
        (self.tmp / "touch.py").write_text("b\n", encoding="utf-8")
        sess = subprocess.run(
            ["node", str(js), "dirty", str(self.tmp), "session"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(sess.returncode, 0, sess.stderr)
        self.assertEqual(sess.stdout.strip(), "touch.py")
        mb = subprocess.run(
            ["node", str(js), "merge-base", str(self.tmp), home],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(mb.returncode, 0, mb.stderr)
        self.assertEqual(mb.stdout.strip(), base)
        prfiles = subprocess.run(
            ["node", str(js), "dirty-at", str(self.tmp), base],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(prfiles.returncode, 0, prfiles.stderr)
        names = {n for n in prfiles.stdout.splitlines() if n.strip()}
        self.assertEqual(names, {"extra.py", "touch.py"})
        fallback = subprocess.run(
            ["node", str(js), "dirty", str(self.tmp), "pr"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(fallback.stdout.strip(), "touch.py")


class TestReviewExtensionManifest(unittest.TestCase):
    def test_session_review_view(self) -> None:
        pkg = json.loads((ROOT / "extensions" / "alexs-rig-review" / "package.json").read_text(encoding="utf-8"))
        views = pkg["contributes"]["views"]["scm"]
        self.assertEqual(views[0]["id"], "alexsRig.review")
        self.assertEqual(views[0]["name"], "Review")
        cmds = {c["command"] for c in pkg["contributes"]["commands"]}
        self.assertIn("alexsRig.review.usePr", cmds)
        self.assertIn("alexsRig.review.useSession", cmds)
        self.assertIn("checkbox", (ROOT / "extensions" / "alexs-rig-review" / "extension.js").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
