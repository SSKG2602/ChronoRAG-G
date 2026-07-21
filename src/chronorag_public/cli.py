"""Minimal public validator CLI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .schemas import EvidenceObligation
from .validators import validate_obligations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.task.read_text(encoding="utf-8"))
    obligations = [EvidenceObligation(**item) for item in payload["obligations"]]
    validate_obligations(obligations)
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
