#!/usr/bin/env python3
"""Tests for Rig hooks: hygiene, L0-miss, Stop review reminder."""

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

import secret_hygiene as hyg  # noqa: E402
import stop_review as stop  # noqa: E402
from session_base import mark_stop_reminded  # noqa: E402


def _run_hook(
    name: str, stdin: str = "", cwd: Path | None = None, env: dict | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "hooks" / name)],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
        cwd=str(cwd or ROOT),
        env={**os.environ, **env} if env else None,
    )


class TestSecretHygiene(unittest.TestCase):
    def test_deny_cat_env(self) -> None:
        msg = hyg.deny_reason({"tool_name": "Bash", "tool_input": {"command": "cat .env"}})
        self.assertIsNotNone(msg)
        self.assertIn("read", msg or "")

    def test_allow_test_f_env(self) -> None:
        self.assertIsNone(hyg.deny_reason({"tool_name": "Bash", "tool_input": {"command": "test -f .env"}}))

    def test_deny_grep_env(self) -> None:
        msg = hyg.deny_reason({"tool_name": "Bash", "tool_input": {"command": "grep KEY .env"}})
        self.assertIsNotNone(msg)
        self.assertIn("read", msg or "")

    def test_deny_source_env(self) -> None:
        msg = hyg.deny_reason({"tool_name": "Bash", "tool_input": {"command": "source .env"}})
        self.assertIsNotNone(msg)
        self.assertIn("read", msg or "")

    def test_deny_dot_source_env(self) -> None:
        msg = hyg.deny_reason({"tool_name": "Bash", "tool_input": {"command": ". .env"}})
        self.assertIsNotNone(msg)
        self.assertIn("read", msg or "")

    def test_deny_write_env_file(self) -> None:
        msg = hyg.deny_reason({"tool_name": "Write", "tool_input": {"file_path": "/tmp/.env", "contents": "x=1"}})
        self.assertIsNotNone(msg)
        self.assertIn("write", msg or "")

    def test_deny_redirect_env(self) -> None:
        msg = hyg.deny_reason({"tool_name": "Bash", "tool_input": {"command": "echo hi > .env"}})
        self.assertIsNotNone(msg)
        self.assertIn("write", msg or "")

    def test_allow_write_py(self) -> None:
        self.assertIsNone(
            hyg.deny_reason({"tool_name": "Write", "tool_input": {"file_path": "src/foo.py", "contents": "x=1"}})
        )

    def test_cli_prints_deny_json(self) -> None:
        proc = _run_hook("secret_hygiene.py", json.dumps({"tool_name": "Bash", "tool_input": {"command": "cat .env"}}))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["hookSpecificOutput"]["permissionDecision"], "deny")


class TestPromptL0Miss(unittest.TestCase):
    def test_silent_when_l0_exists(self) -> None:
        proc = _run_hook("prompt_l0_miss.py", cwd=ROOT)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "")

    def test_miss_when_no_l0(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        try:
            # Isolate HOME so a real global-memory L0 (~/.alexs-rig/memory) on the
            # dev's machine can't turn this "no L0" case into a hit via the fallback.
            proc = _run_hook("prompt_l0_miss.py", cwd=tmp, env={"HOME": str(tmp)})
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            ctx = payload["hookSpecificOutput"]["additionalContext"]
            self.assertIn("alexs-rig-l0-miss", ctx)
            self.assertNotIn("# L0", ctx)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestFindL0Global(unittest.TestCase):
    def test_global_l0_fallback(self) -> None:
        import inject_l0

        home = Path(tempfile.mkdtemp())
        work = Path(tempfile.mkdtemp())  # no in-project docs/memory
        old_home = os.environ.get("HOME")
        try:
            snap = home / ".alexs-rig" / "memory" / "snapshots"
            snap.mkdir(parents=True)
            (snap / "L0.md").write_text("# L0 global\n", encoding="utf-8")
            os.environ["HOME"] = str(home)
            found = inject_l0.find_l0(work)
            self.assertEqual(found, snap / "L0.md")
        finally:
            if old_home is None:
                os.environ.pop("HOME", None)
            else:
                os.environ["HOME"] = old_home
            shutil.rmtree(home, ignore_errors=True)
            shutil.rmtree(work, ignore_errors=True)


class TestStopReview(unittest.TestCase):
    def test_silent_without_session_base(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        try:
            proc = _run_hook("stop_review.py", "{}", cwd=tmp)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout.strip(), "")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_silent_when_stop_hook_active(self) -> None:
        self.assertEqual(stop.should_remind({"stop_hook_active": True}, ROOT, "abc"), "")

    def test_silent_when_already_reminded(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        try:
            mark_stop_reminded(tmp)
            self.assertEqual(stop.should_remind({}, tmp, "abc"), "")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_reminds_on_dirty_git(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        try:
            env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}  # noqa: E501
            subprocess.run(["git", "init"], cwd=tmp, check=True, capture_output=True)
            (tmp / "a.txt").write_text("one\n", encoding="utf-8")
            subprocess.run(["git", "add", "a.txt"], cwd=tmp, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "init"], cwd=tmp, check=True, capture_output=True, env=env)
            sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tmp, text=True).strip()
            (tmp / ".alexs-rig").mkdir()
            (tmp / ".alexs-rig" / "SESSION_BASE").write_text(sha + "\n", encoding="utf-8")
            (tmp / "a.txt").write_text("two\n", encoding="utf-8")
            proc = _run_hook("stop_review.py", "{}", cwd=tmp)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            ctx = payload["hookSpecificOutput"]["additionalContext"]
            self.assertIn("alexs-rig-review", ctx)
            self.assertIn("+N -M", ctx)
            self.assertNotIn('"decision"', proc.stdout)
            proc2 = _run_hook("stop_review.py", "{}", cwd=tmp)
            self.assertEqual(proc2.stdout.strip(), "")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_review_payload_includes_verify_status_when_present(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        try:
            (tmp / ".alexs-rig").mkdir()
            (tmp / ".alexs-rig" / "verify-status.json").write_text(
                json.dumps({"command": "pytest -q", "ok": True, "ran_at": "2026-08-14T00:00:00+00:00"}),
                encoding="utf-8",
            )
            ctx = stop.review_payload("a.txt | 1 +", tmp)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("last check: PASS — pytest -q", ctx)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_review_payload_omits_verify_status_when_absent(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        try:
            ctx = stop.review_payload("a.txt | 1 +", tmp)["hookSpecificOutput"]["additionalContext"]
            self.assertNotIn("last check:", ctx)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestStyleInject(unittest.TestCase):
    def test_style_block_present_and_absent(self) -> None:
        import inject_l0

        tmp = Path(tempfile.mkdtemp())
        try:
            self.assertEqual(inject_l0.style_context_block(tmp), "")
            (tmp / ".alexs-rig").mkdir()
            (tmp / ".alexs-rig" / "style.md").write_text(
                "Google docstrings; no inline comments.", encoding="utf-8"
            )
            block = inject_l0.style_context_block(tmp)
            self.assertIn("alexs-rig-style", block)
            self.assertIn("Google docstrings", block)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_style_nudge_when_absent_in_repo(self) -> None:
        import inject_l0

        tmp = Path(tempfile.mkdtemp())
        try:
            (tmp / ".git").mkdir()  # looks like a real repo
            block = inject_l0.style_context_block(tmp)
            self.assertIn("style-todo", block)
            self.assertIn(".alexs-rig/style.md", block)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_style_survives_compaction(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        try:
            (tmp / ".git").mkdir()
            (tmp / ".alexs-rig").mkdir()
            (tmp / ".alexs-rig" / "style.md").write_text("Google docstrings.", encoding="utf-8")
            proc = _run_hook("reinject_l0.py", "{}", cwd=tmp)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            ctx = json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("alexs-rig-style", ctx)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestSessionBaseNonGit(unittest.TestCase):
    def test_no_snapshot_and_no_litter_outside_repo(self) -> None:
        from session_base import worktree_tree_sha

        tmp = Path(tempfile.mkdtemp())
        try:
            self.assertEqual(worktree_tree_sha(tmp), "")
            self.assertFalse((tmp / ".alexs-rig").exists())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
