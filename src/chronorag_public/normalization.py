"""Small public normalization helpers for synthetic examples."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation


SPACE_RE = re.compile(r"\s+")


def normalize_entity(value: str) -> str:
    return SPACE_RE.sub(" ", value.strip()).casefold()


def normalize_metric(value: str) -> str:
    return SPACE_RE.sub(" ", value.replace("_", " ").strip()).casefold()


def normalize_period(value: str) -> str:
    return SPACE_RE.sub(" ", value.strip().upper())


def normalize_key(entity: str, metric: str, period: str) -> tuple[str, str, str]:
    return (normalize_entity(entity), normalize_metric(metric), normalize_period(period))


def parse_percent(value: str) -> Decimal:
    text = value.strip().removesuffix("%")
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"not a percentage: {value!r}") from exc


def display_value(value: str) -> str:
    return SPACE_RE.sub(" ", value.strip())
