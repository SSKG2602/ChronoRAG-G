"""Toy deterministic evidence registry for synthetic records."""

from __future__ import annotations

from collections import defaultdict

from .normalization import normalize_key
from .schemas import EvidenceCandidate, EvidenceObligation, TemporalRecord


class EvidenceRegistry:
    def __init__(self) -> None:
        self._records: list[TemporalRecord] = []
        self._by_key: dict[tuple[str, str, str], list[TemporalRecord]] = defaultdict(list)

    def add_record(self, record: TemporalRecord) -> None:
        key = normalize_key(record.entity, record.metric, record.target_period)
        self._records.append(record)
        self._by_key[key].append(record)
        self._by_key[key].sort(key=lambda item: item.record_id)

    def candidates_for(self, obligation: EvidenceObligation) -> list[EvidenceCandidate]:
        key = normalize_key(obligation.entity, obligation.metric, obligation.requested_period)
        records = self._by_key.get(key, [])
        return [
            EvidenceCandidate(
                candidate_id=f"synthetic-{obligation.obligation_id}-{index + 1}",
                obligation_id=obligation.obligation_id,
                record=record,
            )
            for index, record in enumerate(records)
        ]

    @property
    def records(self) -> tuple[TemporalRecord, ...]:
        return tuple(self._records)
