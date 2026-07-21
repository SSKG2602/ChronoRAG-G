"""Frozen public result invariants."""

from __future__ import annotations

PUBLIC_METRICS = {
    "total": 1005,
    "accepted": 811,
    "rejected": 194,
    "strict_trace_slot_coverage": (846, 882),
    "micro_required_slot_coverage": (3837, 3889),
    "hybrid_evidence_resolution": (978, 1005),
    "trace_complete_rejected": (167, 194),
    "single_time_enumeration_rejected": (112, 194),
}


def percent(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    return round((numerator / denominator) * 100, 4)


def assert_public_metrics(metrics: dict[str, object]) -> None:
    for key, expected in PUBLIC_METRICS.items():
        if metrics.get(key) != expected:
            raise ValueError(f"metric mismatch for {key}: {metrics.get(key)!r} != {expected!r}")
