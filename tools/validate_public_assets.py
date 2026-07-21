#!/usr/bin/env python3
"""Validate public table and figure triplets."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    tables = ROOT / "tables"
    figures = ROOT / "figures"
    table_stems = sorted(path.stem for path in tables.glob("*.csv"))
    figure_stems = sorted(path.stem for path in figures.glob("*.svg") if path.name[:2].isdigit())
    assert len(table_stems) == 17, len(table_stems)
    assert len(figure_stems) == 8, len(figure_stems)
    for stem in table_stems:
        for ext in [".csv", ".md", ".tex"]:
            assert (tables / f"{stem}{ext}").exists(), stem
    for stem in figure_stems:
        for ext in [".svg", ".png", ".pdf"]:
            assert (figures / f"{stem}{ext}").exists(), stem
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
