#!/usr/bin/env python3
"""Honest detector benchmark: real turns, blind labels, held-out split.

The synthetic benchmark (evals/detector) was written by the same author as the
detector and then the detector was widened until it passed — i.e. tuned on its own
test set. This one avoids that:

* **Real data.** Turns come from your own Claude Code transcripts, not invented cases.
* **Held out.** Only turns after --since (default: the date the cue analysis that
  informed the detector was done), so the detector was never fitted to them.
* **Blind labels.** You label; the score is never shown while labelling.
* **Context shown.** Each turn is labelled next to the agent turn it replies to,
  because most corrections are deictic ("no, not like that").
* **Rare-class aware.** Corrections are ~10% of turns, so sampling is stratified by
  whether the detector fires and estimates are reweighted back to the population.
* **Private.** Everything lands in evals/private/ (gitignored). Nothing is published.

    python3 evals/honest/bench.py sample            # build a stratified sample
    python3 evals/honest/bench.py label             # blind labelling (resumable)
    python3 evals/honest/bench.py score             # precision/recall + CIs

Caveat that cannot be engineered away: the `pending` signal (unreviewed edits present)
depends on git state at that moment and cannot be replayed, so this measures the
text-only detector. Live behaviour is at least this good, not worse.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import random
import re
import sys
from pathlib import Path

RIG = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RIG / "hooks"))
import capture_correction as cc  # noqa: E402

OUT = RIG / "evals" / "private"
SAMPLE = OUT / "sample.jsonl"
LABELS = OUT / "labels.jsonl"
TRANSCRIPTS = Path.home() / ".claude" / "projects"
# The detector's signals were fitted to Cursor history plus self-authored synthetic
# cases. Claude Code transcripts were never used to tune it, so all of them are held
# out; the default keeps the whole pool because firing turns are rare (~2% of turns).
DEFAULT_SINCE = "2000-01-01"

DEFINITION = """A turn counts as a CORRECTION when you were redirecting the agent:
rejecting or overriding what it did or proposed, or stating how it should work.
It is NOT a correction when you are asking a new question, giving a fresh task,
approving, or just adding information."""


# ---------------------------------------------------------------- sample

def iter_turns(since: str):
    """Yield (turn_text, assistant_before, meta) for real user turns after `since`."""
    for f in sorted(glob.glob(str(TRANSCRIPTS / "*" / "*.jsonl"))):
        prev = ""
        try:
            lines = open(f, errors="replace").read().splitlines()
        except OSError:
            continue
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            t, msg = o.get("type"), (o.get("message") or {})
            content = msg.get("content")
            text = ""
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                text = " ".join(
                    c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"
                )
            text = text.strip()
            if t == "assistant":
                if text:
                    prev = text
            elif t == "user" and text:
                ts = str(o.get("timestamp") or "")
                cwd = str(o.get("cwd") or "")
                # Skip headless eval/benchmark runs of our own (they execute in temp
                # dirs); their prompts are synthetic, not turns the user typed.
                if cwd.startswith(("/tmp", "/private/tmp", "/var/folders")):
                    continue
                if ts[:10] >= since and 4 <= len(text) <= 4000 and not cc.is_system_text(text):
                    yield text, prev, {
                        "ts": ts,
                        "cwd": o.get("cwd", ""),
                        "session": o.get("sessionId", ""),
                    }


def cmd_sample(args) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fires, quiet, seen = [], [], set()
    for text, prev, meta in iter_turns(args.since):
        key = re.sub(r"\s+", " ", text).strip().lower()[:120]
        if key in seen:
            continue
        seen.add(key)
        row = {"text": text, "assistant_before": prev, **meta}
        # Stratify on the text-only score: `pending` cannot be replayed from history.
        (fires if cc.score_correction(text)[0] >= cc.THRESHOLD else quiet).append(row)

    rng = random.Random(args.seed)
    # The firing stratum is small (corrections are rare), so label all of it: a census
    # removes sampling error from the precision estimate, which is the tighter claim.
    n_a = len(fires) if args.census_fires else min(args.per_stratum, len(fires))
    n_b = min(args.per_stratum, len(quiet))
    pick = [{**r, "stratum": "fires"} for r in rng.sample(fires, n_a)]
    pick += [{**r, "stratum": "quiet"} for r in rng.sample(quiet, n_b)]
    rng.shuffle(pick)  # interleave so labelling cannot infer the stratum

    header = {"_meta": True, "since": args.since, "seed": args.seed,
              "pop_fires": len(fires), "pop_quiet": len(quiet), "n_fires": n_a, "n_quiet": n_b}
    with SAMPLE.open("w", encoding="utf-8") as f:
        f.write(json.dumps(header) + "\n")
        for r in pick:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"population since {args.since}: {len(fires)} fire / {len(quiet)} do not "
          f"(base rate {100*len(fires)/max(1,len(fires)+len(quiet)):.1f}%)")
    print(f"sampled {n_a} + {n_b} = {len(pick)} turns -> {SAMPLE}")
    print("next: python3 evals/honest/bench.py label")


# ---------------------------------------------------------------- label

def _load_sample():
    rows = [json.loads(x) for x in SAMPLE.read_text(encoding="utf-8").splitlines() if x.strip()]
    return rows[0], rows[1:]


def cmd_label(args) -> None:
    if not SAMPLE.is_file():
        raise SystemExit("no sample yet - run: bench.py sample")
    meta, rows = _load_sample()
    done = {}
    if LABELS.is_file():
        for x in LABELS.read_text(encoding="utf-8").splitlines():
            if x.strip():
                d = json.loads(x)
                done[d["key"]] = d["label"]
    todo = [r for r in rows if r["ts"] + r["text"][:40] not in done]
    print(f"\n{DEFINITION}\n")
    print(f"{len(done)} labelled, {len(todo)} to go.  [y]=correction  [n]=not  [s]=skip  [q]=save+quit\n")
    with LABELS.open("a", encoding="utf-8") as out:
        for i, r in enumerate(todo, 1):
            print("=" * 72)
            print(f"({i}/{len(todo)})  {r['ts'][:16]}  {os.path.basename(r['cwd'])}")
            prev = " ".join(r["assistant_before"].split())
            print(f"\n  AGENT BEFORE: {prev[:400] or '(none)'}")
            print(f"\n  YOU:          {' '.join(r['text'].split())[:400]}\n")
            ans = ""
            while ans not in ("y", "n", "s", "q"):
                ans = input("  correction? [y/n/s/q] ").strip().lower()
            if ans == "q":
                break
            if ans == "s":
                continue
            out.write(json.dumps({"key": r["ts"] + r["text"][:40], "stratum": r["stratum"],
                                  "label": 1 if ans == "y" else 0}) + "\n")
            out.flush()
    print(f"\nsaved -> {LABELS}\nnext: python3 evals/honest/bench.py score")


# ---------------------------------------------------------------- score

def _wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))


def cmd_score(args) -> None:
    if not LABELS.is_file():
        raise SystemExit("no labels yet - run: bench.py label")
    meta, rows = _load_sample()
    by_key = {r["ts"] + r["text"][:40]: r for r in rows}
    labs = [json.loads(x) for x in LABELS.read_text(encoding="utf-8").splitlines() if x.strip()]
    if not labs:
        raise SystemExit("labels file is empty")

    def stats(stratum):
        s = [x for x in labs if x["stratum"] == stratum]
        return sum(x["label"] for x in s), len(s)

    pos_a, n_a = stats("fires")
    pos_b, n_b = stats("quiet")
    N_a, N_b = meta["pop_fires"], meta["pop_quiet"]
    if not n_a or not n_b:
        raise SystemExit("need labels in both strata")

    rate_a, rate_b = pos_a / n_a, pos_b / n_b
    tp, fp = N_a * rate_a, N_a * (1 - rate_a)
    fn = N_b * rate_b
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    # bootstrap recall/f1 CI by resampling the labelled turns within each stratum
    rng = random.Random(0)
    la = [x["label"] for x in labs if x["stratum"] == "fires"]
    lb = [x["label"] for x in labs if x["stratum"] == "quiet"]
    rs, fs = [], []
    for _ in range(2000):
        ra = sum(rng.choice(la) for _ in la) / len(la)
        rb = sum(rng.choice(lb) for _ in lb) / len(lb)
        t, f_, n_ = N_a * ra, N_a * (1 - ra), N_b * rb
        p_ = t / (t + f_) if t + f_ else 0.0
        r_ = t / (t + n_) if t + n_ else 0.0
        rs.append(r_)
        fs.append(2 * p_ * r_ / (p_ + r_) if p_ + r_ else 0.0)
    rs.sort()
    fs.sort()
    pl, ph = _wilson(pos_a, n_a)

    print(f"labelled: {n_a} of {N_a} firing turns, {n_b} of {N_b} non-firing "
          f"(held out since {meta['since']})")
    print(f"estimated corrections in the population: {tp + fn:.0f} of {N_a + N_b} turns "
          f"({100 * (tp + fn) / (N_a + N_b):.1f}%)\n")
    print(f"  precision {precision:.2f}   95% CI [{pl:.2f}, {ph:.2f}]")
    print(f"  recall    {recall:.2f}   95% CI [{rs[50]:.2f}, {rs[1949]:.2f}]")
    print(f"  F1        {f1:.2f}   95% CI [{fs[50]:.2f}, {fs[1949]:.2f}]")
    print("\ntext-only detector (the `pending` signal cannot be replayed from history)")

    if args.examples:
        print("\n--- corrections the detector missed (labelled yes, did not fire) ---")
        shown = 0
        for x in labs:
            if x["label"] == 1 and x["stratum"] == "quiet" and x["key"] in by_key:
                print(f"  · {' '.join(by_key[x['key']]['text'].split())[:100]}")
                shown += 1
                if shown >= 8:
                    break


def cmd_audit(args) -> None:
    """Spot-check somebody else's labels and report agreement (Cohen's kappa)."""
    meta, rows = _load_sample()
    by_key = {r["ts"] + r["text"][:40]: r for r in rows}
    labs = [json.loads(x) for x in LABELS.read_text(encoding="utf-8").splitlines() if x.strip()]
    theirs = {x["key"]: x["label"] for x in labs}
    audit_path = OUT / "audit.jsonl"
    done = set()
    if audit_path.is_file():
        done = {json.loads(x)["key"] for x in audit_path.read_text(encoding="utf-8").splitlines() if x.strip()}
    pool = [k for k in theirs if k in by_key and k not in done]
    random.Random(args.seed).shuffle(pool)
    pool = pool[: args.n]
    print(f"\n{DEFINITION}\n")
    print(f"Spot-checking {len(pool)} labels. The other annotator's answer is hidden.\n")
    with audit_path.open("a", encoding="utf-8") as out:
        for i, k in enumerate(pool, 1):
            r = by_key[k]
            print("=" * 72)
            print(f"({i}/{len(pool)})  {os.path.basename(r['cwd'])}")
            print(f"\n  AGENT BEFORE: {' '.join(r['assistant_before'].split())[:400] or '(none)'}")
            print(f"\n  YOU:          {' '.join(r['text'].split())[:400]}\n")
            ans = ""
            while ans not in ("y", "n", "q"):
                ans = input("  correction? [y/n/q] ").strip().lower()
            if ans == "q":
                break
            out.write(json.dumps({"key": k, "label": 1 if ans == "y" else 0}) + "\n")
            out.flush()
    mine = [json.loads(x) for x in audit_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    both = [(theirs[m["key"]], m["label"]) for m in mine if m["key"] in theirs]
    if not both:
        return
    agree = sum(1 for a, b in both if a == b) / len(both)
    pa = sum(a for a, _ in both) / len(both)
    pb = sum(b for _, b in both) / len(both)
    exp = pa * pb + (1 - pa) * (1 - pb)
    kappa = (agree - exp) / (1 - exp) if exp < 1 else 1.0
    print(f"\nagreement {agree:.0%} on {len(both)} items · Cohen's kappa {kappa:.2f}")
    print("  kappa > 0.7 = the existing labels are credible; lower = relabel yourself")
    dis = [(k, theirs[k]) for k in [m["key"] for m in mine] if k in theirs]
    shown = 0
    for m in mine:
        if m["key"] in theirs and theirs[m["key"]] != m["label"]:
            if shown == 0:
                print("\n  disagreements:")
            print(f"   · you={m['label']} other={theirs[m['key']]} | "
                  f"{' '.join(by_key[m['key']]['text'].split())[:80]}")
            shown += 1
    del dis


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample", help="build a stratified sample from real transcripts")
    s.add_argument("--since", default=DEFAULT_SINCE, help=f"held-out cutoff (default {DEFAULT_SINCE})")
    s.add_argument("--per-stratum", type=int, default=60, help="turns to sample per stratum")
    s.add_argument("--seed", type=int, default=1)
    s.add_argument("--no-census-fires", dest="census_fires", action="store_false",
                   help="sample the firing stratum instead of labelling all of it")
    s.set_defaults(census_fires=True)
    s.set_defaults(func=cmd_sample)
    la = sub.add_parser("label", help="blind labelling, resumable")
    la.set_defaults(func=cmd_label)
    sc = sub.add_parser("score", help="precision/recall with CIs")
    sc.add_argument("--examples", action="store_true", help="show missed corrections")
    sc.set_defaults(func=cmd_score)
    au = sub.add_parser("audit", help="spot-check existing labels, report kappa")
    au.add_argument("-n", type=int, default=20, help="how many to check")
    au.add_argument("--seed", type=int, default=7)
    au.set_defaults(func=cmd_audit)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
