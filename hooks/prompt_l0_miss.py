#!/usr/bin/env python3
"""UserPromptSubmit: one-line miss if this project has no L0. Never dump L0."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inject_l0 import find_l0  # noqa: E402


MISS = (
    "<alexs-rig-l0-miss>No docs/memory/snapshots/L0.md in this project. "
    "Standing memory is not loaded here — run bin/l0-regen --root . if you want it. "
    "Do not invent principles.</alexs-rig-l0-miss>"
)


def miss_payload() -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": MISS,
        }
    }


def main() -> None:
    if find_l0(Path.cwd()) is not None:
        return
    print(json.dumps(miss_payload()))


if __name__ == "__main__":
    main()
