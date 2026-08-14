#!/usr/bin/env python3
"""Measure the harness's impact on QUALITY and TOKENS via a with/without ablation.

For each synthetic task, run a headless agent twice — plugin disabled (baseline) and
enabled (treatment) — capture the response and its token cost, and grade adherence +
correctness. Report the deltas: does the rig change behavior, and at what token cost?

SAFETY: dry-run by default (no agent calls). Real runs need --run AND a hard
--budget-usd ceiling; both arms + the grader use a cheap model. Cases are synthetic
(no real conversations). Reports are printed locally; nothing is published.

    python3 evals/calibrate/run.py                       # dry-run: show the plan + estimate
    python3 evals/calibrate/run.py --run --budget-usd 0.50
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

TASKS = Path(__file__).with_name("tasks.json")
PLUGIN = "alexs-rig@alexs-rig"
CHEAP = "claude-haiku-4-5-20251001"


def load_tasks() -> list[dict]:
    return json.loads(TASKS.read_text(encoding="utf-8"))


def _claude_json(prompt: str, model: str, cwd: str) -> tuple[str, float]:
    """Run `claude -p --output-format json`; return (result_text, cost_usd)."""
    proc = subprocess.run(
        ["claude", "-p", "--model", model, "--output-format", "json", prompt],
        cwd=cwd, capture_output=True, text=True, check=False,
    )
    out = proc.stdout.strip()
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return out, 0.0
    if isinstance(data, dict):
        return str(data.get("result", out)), float(data.get("total_cost_usd", 0.0) or 0.0)
    return out, 0.0


def _toggle_plugin(enabled: bool) -> None:
    subprocess.run(
        ["claude", "plugin", "enable" if enabled else "disable", PLUGIN],
        capture_output=True, text=True, check=False,
    )


def _grade(task: dict, response: str, judge: str) -> tuple[int, int, float]:
    prompt = (
        "You are grading an assistant response. Reply with ONLY a JSON object "
        '{"adherence": 0 or 1, "correctness": 0 or 1}.\n\n'
        f"TASK: {task['prompt']}\n"
        f"ADHERENCE means: {task['adherence']}\n"
        f"CORRECTNESS means: {task['correctness']}\n\n"
        f"RESPONSE:\n{response[:2000]}"
    )
    text, cost = _claude_json(prompt, judge, cwd=".")
    adh = cor = 0
    try:
        m = json.loads(text[text.find("{"): text.rfind("}") + 1])
        adh, cor = int(bool(m.get("adherence"))), int(bool(m.get("correctness")))
    except (json.JSONDecodeError, ValueError):
        pass
    return adh, cor, cost


def dry_run(tasks: list[dict]) -> None:
    print(f"DRY RUN — {len(tasks)} tasks x 2 arms (off/on) + a grader each = {len(tasks) * 4} agent calls.")
    print("No agent calls made. Re-run with --run --budget-usd <cap> to execute.\n")
    for t in tasks:
        print(f"[{t['id']}] tests {t['principle']}")
        print(f"  prompt:    {t['prompt']}")
        print(f"  off-arm:   claude plugin disable {PLUGIN}; claude -p <prompt>")
        print(f"  on-arm:    claude plugin enable  {PLUGIN}; claude -p <prompt>")
        print(f"  grade on:  adherence={t['adherence'][:60]}…\n")
    print("Rough cost: a few short haiku calls per task — cents / minimal plan usage.")


def real_run(tasks: list[dict], model: str, judge: str, budget: float) -> None:
    spent = 0.0
    rows: list[dict] = []
    try:
        for t in tasks:
            rec = {"id": t["id"], "principle": t["principle"]}
            for arm, enabled in (("off", False), ("on", True)):
                if spent >= budget:
                    print(f"\n⚠ budget ${budget:.2f} reached (spent ${spent:.4f}) — stopping early.")
                    _report(rows, spent)
                    return
                _toggle_plugin(enabled)
                work = tempfile.mkdtemp()
                try:
                    text, c1 = _claude_json(t["prompt"], model, cwd=work)
                finally:
                    shutil.rmtree(work, ignore_errors=True)
                adh, cor, c2 = _grade(t, text, judge)
                spent += c1 + c2
                rec[arm] = {"adherence": adh, "correctness": cor, "cost": c1}
                print(f"[{t['id']}] {arm}: adherence={adh} correctness={cor} cost=${c1:.4f}")
            rows.append(rec)
    finally:
        _toggle_plugin(True)  # always restore
    _report(rows, spent)


def _report(rows: list[dict], spent: float) -> None:
    if not rows:
        print("no results.")
        return
    da = dc = dt = 0.0
    print("\n=== impact (on − off), weighted quality = 0.5*adherence + 0.5*correctness ===")
    for r in rows:
        if "off" not in r or "on" not in r:
            continue
        a = r["on"]["adherence"] - r["off"]["adherence"]
        c = r["on"]["correctness"] - r["off"]["correctness"]
        tok = r["on"]["cost"] - r["off"]["cost"]
        da += a
        dc += c
        dt += tok
        print(f"  {r['id']:16} {r['principle']:9} Δadherence={a:+d} Δcorrectness={c:+d} Δcost=${tok:+.4f}")
    n = len([r for r in rows if "off" in r and "on" in r]) or 1
    print(f"\nmean Δadherence={da/n:+.2f}  mean Δcorrectness={dc/n:+.2f}  "
          f"mean Δquality={(0.5*da+0.5*dc)/n:+.2f}  mean Δcost/task=${dt/n:+.4f}")
    print(f"total spent this run: ${spent:.4f}")


def main() -> None:
    ap = argparse.ArgumentParser(description="With/without ablation: harness impact on quality + tokens")
    ap.add_argument("--run", action="store_true", help="Actually run (spends tokens). Default: dry-run.")
    ap.add_argument("--budget-usd", type=float, default=0.0, help="Hard cost ceiling; required with --run.")
    ap.add_argument("--model", default=CHEAP, help=f"Model for both arms (default cheap: {CHEAP}).")
    ap.add_argument("--judge-model", default=CHEAP, help="Grader model (default cheap).")
    args = ap.parse_args()
    tasks = load_tasks()
    if not args.run:
        dry_run(tasks)
        return
    if args.budget_usd <= 0:
        raise SystemExit("--run requires a positive --budget-usd ceiling (be careful with spend).")
    if not shutil.which("claude"):
        raise SystemExit("claude CLI not found.")
    real_run(tasks, args.model, args.judge_model, args.budget_usd)


if __name__ == "__main__":
    main()
