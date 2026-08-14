#!/usr/bin/env python3
"""Deterministic benchmark for the correction-capture detector — ZERO LLM tokens.

Runs the (pure-Python) score_correction heuristic over a SYNTHETIC labeled set
and reports precision / recall / F1 at the capture threshold. No real user
conversations are used (privacy) and no model is called (cost). Corrections in
real use usually coincide with fresh unreviewed edits, so we report both
`pending=False` (text signal only) and `pending=True`.

    python3 evals/detector/bench.py
"""

from __future__ import annotations

import json
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
cc = SourceFileLoader("capture_correction", str(ROOT / "hooks" / "capture_correction.py")).load_module()
DATA = Path(__file__).with_name("dataset.jsonl")


def load() -> list[dict]:
    return [json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip()]


def score(rows: list[dict], pending: bool) -> dict:
    tp = fp = fn = tn = 0
    missed: list[str] = []
    for r in rows:
        s, _ = cc.score_correction(r["text"], pending=pending)
        pred = 1 if s >= cc.THRESHOLD else 0
        if pred and r["label"]:
            tp += 1
        elif pred and not r["label"]:
            fp += 1
        elif not pred and r["label"]:
            fn += 1
            missed.append(r["text"])
        else:
            tn += 1
    prec = tp / (tp + fp) if (tp + fp) else 1.0
    rec = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": prec, "recall": rec, "f1": f1, "missed": missed}


def main() -> None:
    rows = load()
    pos = sum(r["label"] for r in rows)
    print(f"detector benchmark — {len(rows)} synthetic cases ({pos} corrections, {len(rows) - pos} normal), "
          f"threshold={cc.THRESHOLD}")
    for pending in (False, True):
        m = score(rows, pending)
        print(f"\npending={pending}:  precision={m['precision']:.2f}  recall={m['recall']:.2f}  f1={m['f1']:.2f}  "
              f"(tp={m['tp']} fp={m['fp']} fn={m['fn']} tn={m['tn']})")
        if m["missed"]:
            print("  missed corrections:")
            for t in m["missed"]:
                print(f"    - {t}")


if __name__ == "__main__":
    main()
