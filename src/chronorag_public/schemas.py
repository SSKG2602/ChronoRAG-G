"""Public-safe synthetic data schemas."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True)
class TemporalRecord:
    record_id: str
    entity: str
    metric: str
    target_period: str
    value: str
    statement_period: str
    source_title: str = "Synthetic earnings note"
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class EvidenceObligation:
    obligation_id: str
    entity: str
    metric: str
    requested_period: str
    required: bool = True
    label: str = ""


@dataclass(frozen=True)
class EvidenceCandidate:
    candidate_id: str
    obligation_id: str
    record: TemporalRecord


@dataclass(frozen=True)
class SlotAllocation:
    obligation_id: str
    candidate_id: str
    selected: bool


@dataclass(frozen=True)
class AssembledAnswer:
    values_by_obligation: Mapping[str, str]
    missing_obligations: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return not self.missing_obligations
