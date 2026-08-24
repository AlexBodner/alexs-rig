#!/usr/bin/env python3
"""Measure an LLM classifier on the same labelled turns as the regex detector.

The regex detector measured badly (recall ~0.05). Replacing it with an LLM pass at
flush time only makes sense if the LLM measures better — on the *same* ground truth,
not on a fresh set. This runs the LLM over the labelled sample and reports precision /
recall with the same stratified reweighting, so the two are directly comparable.

Turns are sent in batches, which is both cheaper (one agent session per batch instead
of per turn) and closer to how the flush would actually work.

    python3 evals/honest/llm_classifier.py --budget-usd 1
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

RIG = Path(__file__).resolve().parents[2]
PRIV = RIG / "evals" / "private"
CHEAP = "claude-haiku-4-5-20251001"

DEFINITION = (
    "A turn is a CORRECTION when the user is redirecting the agent: explicitly rejecting "
    "or overriding what it did or proposed, or declaring something wrong. It is NOT a "
    "correction when the user asks a question (even a sceptical or challenging one), asks "
    "for an explanation, gives a new instruction or task, approves, or adds information. "
    "Turns may be in English or Spanish."
)


def load():
    rows = [json.loads(x) for x in (PRIV / "sample.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    meta, items = rows[0], rows[1:]
    labs = {json.loads(x)["key"]: json.loads(x) for x in (PRIV / "labels.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()}
    data = []
    for r in items:
        k = r["ts"] + r["text"][:40]
        if k in labs:
            data.append({"text": r["text"], "prev": r["assistant_before"],
                         "label": labs[k]["label"], "stratum": r["stratum"]})
    return meta, data


def ask(batch, model):
    lines = []
    for i, d in enumerate(batch, 1):
        prev = " ".join(d["prev"].split())[:400] or "(none)"
        you = " ".join(d["text"].split())[:400]
        lines.append(f"--- {i} ---\nAGENT SAID: {prev}\nUSER REPLIED: {you}")
    prompt = (
        f"{DEFINITION}\n\nClassify each numbered exchange. Reply with ONLY a JSON object "
        f'mapping the number to 1 (correction) or 0 (not), e.g. {{"1":0,"2":1}}. '
        f"No prose.\n\n" + "\n".join(lines)
    )
    p = subprocess.run(["claude", "-p", "--model", model, "--output-format", "json", prompt],
                       capture_output=True, text=True, check=False)
    try:
        d = json.loads(p.stdout)
        text, cost = str(d.get("result", "")), float(d.get("total_cost_usd", 0) or 0)
    except json.JSONDecodeError:
        return {}, 0.0
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return {}, cost
    try:
        return {int(k): int(v) for k, v in json.loads(m.group(0)).items()}, cost
    except (ValueError, json.JSONDecodeError):
        return {}, cost


def main() -> None:
    ap = argparse.ArgumentParser(description="Measure an LLM classifier on the labelled turns")
    ap.add_argument("--budget-usd", type=float, default=1.0, help="hard ceiling")
    ap.add_argument("--batch", type=int, default=18)
    ap.add_argument("--model", default=CHEAP)
    args = ap.parse_args()
    meta, data = load()
    if not data:
        raise SystemExit("no labelled data - run bench.py sample/label first")

    preds, spent = {}, 0.0
    for start in range(0, len(data), args.batch):
        if spent >= args.budget_usd:
            print(f"budget ${args.budget_usd} reached, stopping early")
            break
        batch = data[start:start + args.batch]
        got, cost = ask(batch, args.model)
        spent += cost
        for i, d in enumerate(batch, 1):
            if i in got:
                preds[start + i - 1] = got[i]
        print(f"  batch {start // args.batch + 1}: {len(got)}/{len(batch)} classified  (${spent:.3f})", flush=True)

    n_a = sum(1 for d in data if d["stratum"] == "fires")
    n_b = len(data) - n_a
    W = {"fires": meta["pop_fires"] / n_a, "quiet": meta["pop_quiet"] / n_b}
    tp = fp = fn = 0.0
    scored = 0
    for i, d in enumerate(data):
        if i not in preds:
            continue
        scored += 1
        w, hit, lab = W[d["stratum"]], preds[i], d["label"]
        if hit and lab:
            tp += w
        elif hit and not lab:
            fp += w
        elif not hit and lab:
            fn += w
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    print(f"\nLLM classifier on {scored} labelled turns (reweighted to {meta['pop_fires'] + meta['pop_quiet']}):")
    print(f"  precision {p:.2f}   recall {r:.2f}   F1 {f1:.2f}")
    print(f"  cost ${spent:.3f} for {scored} turns  ->  ${spent / max(1, scored) * 300:.2f} per 300-turn flush")
    print("\n  regex detector, same ground truth:  precision 0.57  recall 0.05  F1 0.10")


if __name__ == "__main__":
    main()
