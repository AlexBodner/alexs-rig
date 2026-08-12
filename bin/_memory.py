#!/usr/bin/env python3
"""Shared helpers for Alex's Rig memory CLIs."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEMORY = ROOT / "docs" / "memory"
SNAPSHOTS = MEMORY / "snapshots"
ARCHIVE = MEMORY / "archive"
L0_BUDGET_TOKENS = int(os.environ.get("L0_BUDGET_TOKENS", "1200"))
CHARS_PER_TOKEN = 4


def configure_paths(root: Path | str | None = None) -> Path:
    """Point MEMORY at a project (or docs/memory) root.

    Resolution order: explicit ``root`` → ``ALEXS_RIG_MEMORY`` → ``ALEXS_RIG_ROOT`` →
    directory containing this ``bin/`` (the alexs-rig checkout).

    ``root`` may be the project root (expects ``docs/memory/``) or the ``docs/memory``
    directory itself.
    """
    global ROOT, MEMORY, SNAPSHOTS, ARCHIVE
    if root is None:
        env = os.environ.get("ALEXS_RIG_MEMORY") or os.environ.get("ALEXS_RIG_ROOT")
        root = Path(env) if env else Path(__file__).resolve().parents[1]
    else:
        root = Path(root)
    root = root.expanduser().resolve()
    if root.name == "memory" and root.parent.name == "docs":
        MEMORY = root
        ROOT = root.parent.parent
    else:
        ROOT = root
        MEMORY = ROOT / "docs" / "memory"
    SNAPSHOTS = MEMORY / "snapshots"
    ARCHIVE = MEMORY / "archive"
    return ROOT


def add_root_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Project root (or docs/memory). Overrides ALEXS_RIG_MEMORY / ALEXS_RIG_ROOT.",
    )


def apply_root_arg(args: argparse.Namespace) -> Path:
    return configure_paths(getattr(args, "root", None))


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_layout() -> None:
    for p in (MEMORY, SNAPSHOTS, ARCHIVE, MEMORY / "mining", MEMORY / "telemetry"):
        p.mkdir(parents=True, exist_ok=True)
    for name in ("PRINCIPLES.jsonl", "PROGRESS.jsonl", "PENDING.jsonl"):
        path = MEMORY / name
        if not path.exists():
            path.write_text("", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def upsert_row(path: Path, row: dict, id_key: str = "id") -> dict:
    ensure_layout()
    rows = read_jsonl(path)
    rid = row[id_key]
    out: list[dict] = []
    found = False
    for existing in rows:
        if existing.get(id_key) == rid:
            merged = {**existing, **row, "updated": utc_now()}
            out.append(merged)
            found = True
        else:
            out.append(existing)
    if not found:
        row = {**row, "updated": utc_now()}
        if "status" not in row and path.name == "PENDING.jsonl":
            row["status"] = "open"
        out.append(row)
    write_jsonl(path, out)
    return row if not found else next(r for r in out if r.get(id_key) == rid)


def archive_row(src: Path, archive_name: str, rid: str, reason: str = "") -> bool:
    rows = read_jsonl(src)
    keep: list[dict] = []
    moved = None
    for row in rows:
        if row.get("id") == rid:
            moved = {**row, "superseded_at": utc_now(), "reason": reason, "status": "archived"}
        else:
            keep.append(row)
    if moved is None:
        return False
    write_jsonl(src, keep)
    arch = ARCHIVE / archive_name
    arch_rows = read_jsonl(arch)
    arch_rows.append(moved)
    write_jsonl(arch, arch_rows)
    return True


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN)


SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|secret|password|token|bearer\s+[a-z0-9\-._~+/]+=*|sk-[a-z0-9]{10,})"
)


def redact(text: str) -> str:
    return SECRET_RE.sub("[REDACTED]", text)


def regen_l0() -> Path:
    ensure_layout()
    principles = [r for r in read_jsonl(MEMORY / "PRINCIPLES.jsonl") if r.get("status", "active") == "active"]
    progress = [r for r in read_jsonl(MEMORY / "PROGRESS.jsonl") if r.get("status", "active") != "closed"]
    pending = [r for r in read_jsonl(MEMORY / "PENDING.jsonl") if r.get("status", "open") == "open"]
    pending_sorted = sorted(pending, key=lambda r: (r.get("priority", "P9"), r.get("updated", "")))
    top = pending_sorted[:5]

    lines = [
        "# L0 — active snapshot (generated; do not hand-edit)",
        "",
        "## PRINCIPLES",
    ]
    if not principles:
        lines.append("- (none yet — run principle-upsert or mine-corrections)")
    for p in principles:
        lines.append(f"- [{p['id']}] {p.get('text', '').strip()}")

    lines += ["", "## PROGRESS"]
    if not progress:
        lines.append("- (none)")
    for f in progress:
        lines.append(
            f"- [{f['id']}] {f.get('status', '?')} | {f.get('summary', '').strip()}"
            + (f" | {f['path']}" if f.get("path") else "")
        )

    lines += ["", "## PENDING", f"open={len(pending)} | showing {len(top)}"]
    if not top:
        lines.append("- (none)")
    for t in top:
        lines.append(f"- [{t['id']}] {t.get('priority', 'P?')} | {t.get('text', '').strip()}")

    body = "\n".join(lines) + "\n"
    tokens = estimate_tokens(body)
    out = SNAPSHOTS / "L0.md"
    if tokens > L0_BUDGET_TOKENS:
        body += (
            f"\n> OVERFLOW tokens≈{tokens} budget={L0_BUDGET_TOKENS} — "
            "distill/forget at source; do not silent-truncate.\n"
        )
    out.write_text(body, encoding="utf-8")

    _write_md_view("PRINCIPLES.md", principles, lambda p: f"- **{p['id']}**: {p.get('text', '')}")
    _write_md_view(
        "PROGRESS.md",
        progress,
        lambda f: f"- **{f['id']}** ({f.get('status', '?')}): {f.get('summary', '')}",
    )
    _write_md_view(
        "PENDING.md",
        pending_sorted,
        lambda t: f"- **{t['id']}** {t.get('priority', '')}: {t.get('text', '')} [{t.get('status', 'open')}]",
    )

    telem = MEMORY / "telemetry" / "l0-size.jsonl"
    with telem.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps({"ts": utc_now(), "tokens": tokens, "chars": len(body), "budget": L0_BUDGET_TOKENS})
            + "\n"
        )
    return out


def _write_md_view(name: str, rows: list[dict], fmt) -> None:
    lines = [f"# {name.replace('.md', '')}", "", "Generated view — prefer upsert CLIs for edits.", ""]
    if not rows:
        lines.append("(empty)")
    else:
        lines.extend(fmt(r) for r in rows)
    (MEMORY / name).write_text("\n".join(lines) + "\n", encoding="utf-8")


# Default paths for import-time (checkout). CLIs call configure_paths() after parsing args.
configure_paths()
