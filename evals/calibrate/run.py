#!/usr/bin/env python3
"""Measure the harness's impact on QUALITY and TOKENS via a with/without ablation.

The clean signal comes from testing NON-DEFAULT preferences: each task carries an
arbitrary rule the base model would not produce on its own (`tasks.json`), injected into
the ON arm's L0. If the rig works, the ON arm follows the rule and the OFF arm doesn't —
graded DETERMINISTICALLY (regex / substring), so there is no judge model and no judge cost,
and the grade is objective. Generic "good practice" tasks show ~0 (the model already does
them); this design isolates the rig's real value — enforcing preferences it wouldn't guess.

SAFETY: dry-run by default (no agent calls). Real runs need --run AND a hard
--budget-usd ceiling. Each headless call is a full agent session, so cost is real
(~$0.20/call on Opus). The plugin is disabled/enabled per arm and restored in a finally.

    python3 evals/calibrate/run.py                             # dry-run: plan + estimate
    python3 evals/calibrate/run.py --run --budget-usd 3 --model claude-opus-4-8
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

SPEC = Path(__file__).with_name("tasks.json")
PLUGIN = "alexs-rig@alexs-rig"
CHEAP = "claude-haiku-4-5-20251001"


def load_spec() -> dict:
    return json.loads(SPEC.read_text(encoding="utf-8"))


def build_l0(rules: list[str]) -> str:
    """Render the injected rules as an L0 snapshot the SessionStart hook will pick up."""
    lines = ["# L0 — active snapshot (generated; do not hand-edit)", "", "## PRINCIPLES"]
    lines += [f"- {r}" for r in rules]
    return "\n".join(lines) + "\n"


def follows(task: dict, response: str) -> bool:
    """Deterministic check that the response obeyed the task's rule."""
    if "regex" in task:
        return bool(re.search(task["regex"], response))
    return task.get("contains", "") in response


def _claude(prompt: str, model: str, cwd: str) -> tuple[str, float]:
    proc = subprocess.run(
        ["claude", "-p", "--model", model, "--output-format", "json", prompt],
        cwd=cwd, capture_output=True, text=True, check=False,
    )
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return proc.stdout, 0.0
    if isinstance(data, dict):
        return str(data.get("result", "")), float(data.get("total_cost_usd", 0.0) or 0.0)
    return proc.stdout, 0.0


def _toggle(enabled: bool) -> None:
    subprocess.run(
        ["claude", "plugin", "enable" if enabled else "disable", PLUGIN],
        capture_output=True, check=False,
    )


def dry_run(spec: dict, repeats: int) -> None:
    tasks = spec["tasks"]
    n = len(tasks) * 2 * repeats
    print(f"DRY RUN — {len(tasks)} tasks x 2 arms x {repeats} repeat(s) = {n} agent calls; "
          "deterministic grading (no judge).")
    print("No agent calls made. Re-run with --run --budget-usd <cap> to execute.\n")
    print("Injected rules (ON arm L0) — arbitrary + non-default on purpose:")
    for r in spec["rules"]:
        print(f"  {r}")
    print()
    for t in tasks:
        chk = t["regex"] if "regex" in t else f"contains {t.get('contains')!r}"
        print(f"[{t['id']}] prompt: {t['prompt']}")
        print(f"           follows-rule check: {chk}")
    print("\nOFF arm: plugin disabled, plain dir. ON arm: plugin enabled, dir seeded with the rules as L0.")


def real_run(spec: dict, model: str, budget: float, repeats: int) -> None:
    rules_l0 = build_l0(spec["rules"])
    tasks = spec["tasks"]
    spent = 0.0
    tally: dict = {}
    stopped = False
    try:
        for arm, enabled in (("off", False), ("on", True)):
            _toggle(enabled)
            for t in tasks:
                hits = runs = 0
                for _ in range(repeats):
                    if spent >= budget:
                        stopped = True
                        break
                    work = tempfile.mkdtemp()
                    if enabled:
                        snap = Path(work) / "docs" / "memory" / "snapshots"
                        snap.mkdir(parents=True)
                        (snap / "L0.md").write_text(rules_l0, encoding="utf-8")
                    try:
                        text, cost = _claude(t["prompt"], model, work)
                    finally:
                        shutil.rmtree(work, ignore_errors=True)
                    spent += cost
                    runs += 1
                    hits += int(follows(t, text))
                tally[(t["id"], arm)] = (hits, runs)
                if runs:
                    print(f"{arm:3} {t['id']:14} {hits}/{runs} followed   (spent ${spent:.2f})", flush=True)
                if stopped:
                    break
            if stopped:
                break
    finally:
        _toggle(True)  # always restore
    _report(tasks, tally, spent, stopped)


def _report(tasks: list[dict], tally: dict, spent: float, stopped: bool) -> None:
    print("\n=== rule adherence: off (no rig) vs on (rig injects the rule) ===")
    deltas = []
    for t in tasks:
        oh, orn = tally.get((t["id"], "off"), (0, 0))
        nh, nrn = tally.get((t["id"], "on"), (0, 0))
        fo = oh / orn if orn else -1.0
        fn = nh / nrn if nrn else -1.0
        if orn and nrn:
            deltas.append(fn - fo)
        print(f"  {t['id']:14} off={fo:+.2f}  on={fn:+.2f}")
    if deltas:
        print(f"\nmean Δadherence = {sum(deltas) / len(deltas):+.2f}  (over {len(deltas)} fully-run tasks)")
    if stopped:
        print("⚠ stopped early on budget — some cells incomplete.")
    print(f"total spent this run: ${spent:.2f}")


def main() -> None:
    ap = argparse.ArgumentParser(description="With/without ablation: harness impact on quality + tokens")
    ap.add_argument("--run", action="store_true", help="Actually run (spends tokens). Default: dry-run.")
    ap.add_argument("--budget-usd", type=float, default=0.0, help="Hard cost ceiling; required with --run.")
    ap.add_argument("--model", default=CHEAP, help=f"Model for both arms (default cheap: {CHEAP}).")
    ap.add_argument("--repeats", type=int, default=1, help="Runs per (task, arm) to average variance.")
    args = ap.parse_args()
    spec = load_spec()
    if not args.run:
        dry_run(spec, args.repeats)
        return
    if args.budget_usd <= 0:
        raise SystemExit("--run requires a positive --budget-usd ceiling (be careful with spend).")
    if not shutil.which("claude"):
        raise SystemExit("claude CLI not found.")
    real_run(spec, args.model, args.budget_usd, args.repeats)


if __name__ == "__main__":
    main()
