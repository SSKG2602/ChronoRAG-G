"""Validation utilities for public-safe synthetic artifacts."""

from __future__ import annotations

from .schemas import EvidenceObligation, TemporalRecord

TRACE_STEPS = (
    "planned_obligation",
    "retrieved_candidates",
    "temporal_decision",
    "selected_evidence",
    "slot_allocation",
    "answer_payload",
    "structured_answer",
    "grounding",
    "rendered_output",
)


def validate_obligations(obligations: list[EvidenceObligation]) -> None:
    seen: set[str] = set()
    for obligation in obligations:
        if not obligation.obligation_id:
            raise ValueError("obligation_id is required")
        if obligation.obligation_id in seen:
            raise ValueError(f"duplicate obligation_id: {obligation.obligation_id}")
        seen.add(obligation.obligation_id)
        if not obligation.entity or not obligation.metric or not obligation.requested_period:
            raise ValueError(f"incomplete obligation: {obligation.obligation_id}")


def validate_record(record: TemporalRecord) -> None:
    if not record.record_id:
        raise ValueError("record_id is required")
    if not record.entity or not record.metric or not record.target_period:
        raise ValueError(f"incomplete record: {record.record_id}")
    if record.statement_period == record.target_period:
        return
    if not record.statement_period:
        raise ValueError(f"statement_period is required: {record.record_id}")


def validate_trace_steps(steps: list[str]) -> None:
    if tuple(steps) != TRACE_STEPS:
        raise ValueError("trace steps must match the public conceptual order")
