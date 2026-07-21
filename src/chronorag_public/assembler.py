"""Toy slot-preserving answer assembly for synthetic examples."""

from __future__ import annotations

from .normalization import display_value
from .registry import EvidenceRegistry
from .schemas import AssembledAnswer, EvidenceObligation


def assemble_slot_preserving_answer(
    obligations: list[EvidenceObligation],
    registry: EvidenceRegistry,
) -> AssembledAnswer:
    values: dict[str, str] = {}
    missing: list[str] = []
    for obligation in obligations:
        candidates = registry.candidates_for(obligation)
        if not candidates:
            if obligation.required:
                missing.append(obligation.obligation_id)
            continue
        values[obligation.obligation_id] = display_value(candidates[0].record.value)
    return AssembledAnswer(values_by_obligation=values, missing_obligations=tuple(missing))


def render_enumeration(obligations: list[EvidenceObligation], answer: AssembledAnswer) -> str:
    parts: list[str] = []
    for obligation in obligations:
        value = answer.values_by_obligation.get(obligation.obligation_id)
        label = obligation.label or f"{obligation.entity} {obligation.metric} {obligation.requested_period}"
        if value is None:
            parts.append(f"{label}: unavailable")
        else:
            parts.append(f"{label}: {value}")
    return "; ".join(parts)
