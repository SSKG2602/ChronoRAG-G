"""Immutable, standard-library-only public interoperability contracts."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, TypeAlias

JSONScalar: TypeAlias = str | int | float | bool | None
_STATUSES = frozenset({"supported", "unsupported", "insufficient_evidence"})


def _bounded(value: Any, label: str, limit: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    if len(value) > limit:
        raise ValueError(f"{label} exceeds {limit} characters")
    return value


def _scalar(value: Any, label: str) -> JSONScalar:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise ValueError(f"{label} must be a JSON scalar")


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return value


def _frozen_mapping(value: Any, label: str) -> tuple[tuple[str, JSONScalar], ...]:
    source = _mapping(value, label)
    if len(source) > 32:
        raise ValueError(f"{label} has more than 32 entries")
    result: list[tuple[str, JSONScalar]] = []
    for key in sorted(source):
        clean_key = _bounded(key, f"{label} key", 128)
        result.append((clean_key, _scalar(source[key], f"{label}.{clean_key}")))
    return tuple(result)


def _load_object(source: str | Path | Mapping[str, Any], label: str) -> Mapping[str, Any]:
    if isinstance(source, (str, Path)):
        value = json.loads(Path(source).read_text(encoding="utf-8"))
    else:
        value = source
    return _mapping(value, label)


def _ordered(mapping_items: tuple[tuple[str, JSONScalar], ...]) -> dict[str, JSONScalar]:
    return {key: value for key, value in mapping_items}


class _Serializable:
    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )


@dataclass(frozen=True, slots=True)
class EvidenceRequirement(_Serializable):
    id: str
    subject: str
    property: str
    temporal_scope: str
    expected_value_type: str
    optional_qualifiers: tuple[tuple[str, JSONScalar], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "subject": self.subject,
            "property": self.property,
            "temporal_scope": self.temporal_scope,
            "expected_value_type": self.expected_value_type,
            "optional_qualifiers": _ordered(self.optional_qualifiers),
        }


@dataclass(frozen=True, slots=True)
class TaskSpec(_Serializable):
    question: str
    requirements: tuple[EvidenceRequirement, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "requirements": [item.to_dict() for item in self.requirements],
        }


@dataclass(frozen=True, slots=True)
class CorpusRecord(_Serializable):
    record_id: str
    text: str
    subject: str
    property: str
    valid_time: str
    source_time: str
    attributes: tuple[tuple[str, JSONScalar], ...] = ()
    supports_requirements: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        result = {
            "record_id": self.record_id,
            "text": self.text,
            "subject": self.subject,
            "property": self.property,
            "valid_time": self.valid_time,
            "source_time": self.source_time,
            "attributes": _ordered(self.attributes),
        }
        if self.supports_requirements:
            result["supports_requirements"] = list(self.supports_requirements)
        return result


@dataclass(frozen=True, slots=True)
class EvidenceRecord(_Serializable):
    evidence_id: str
    text: str
    supports_requirements: tuple[str, ...]
    metadata: tuple[tuple[str, JSONScalar], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "text": self.text,
            "supports_requirements": list(self.supports_requirements),
            "metadata": _ordered(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class EvidencePack(_Serializable):
    requirements: tuple[str, ...]
    records: tuple[EvidenceRecord, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "requirements": list(self.requirements),
            "records": [record.to_dict() for record in self.records],
        }


@dataclass(frozen=True, slots=True)
class AnswerComponent(_Serializable):
    requirement_id: str
    status: str
    value: JSONScalar
    evidence_ids: tuple[str, ...]
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "status": self.status,
            "value": self.value,
            "evidence_ids": list(self.evidence_ids),
            "note": self.note,
        }


@dataclass(frozen=True, slots=True)
class AnswerContract(_Serializable):
    components: tuple[AnswerComponent, ...]
    overall_status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "components": [component.to_dict() for component in self.components],
            "overall_status": self.overall_status,
        }


def _requirement(value: Any) -> EvidenceRequirement:
    item = _mapping(value, "requirement")
    return EvidenceRequirement(
        id=_bounded(item.get("id"), "requirement.id", 32),
        subject=_bounded(item.get("subject"), "requirement.subject", 512),
        property=_bounded(item.get("property"), "requirement.property", 512),
        temporal_scope=_bounded(
            item.get("temporal_scope"), "requirement.temporal_scope", 256
        ),
        expected_value_type=_bounded(
            item.get("expected_value_type"), "requirement.expected_value_type", 128
        ),
        optional_qualifiers=_frozen_mapping(
            item.get("optional_qualifiers", {}), "requirement.optional_qualifiers"
        ),
    )


def load_task_spec(source: str | Path | Mapping[str, Any]) -> TaskSpec:
    value = _load_object(source, "task")
    raw_requirements = value.get("requirements")
    if not isinstance(raw_requirements, list):
        raise ValueError("task.requirements must be an array")
    task = TaskSpec(
        question=_bounded(value.get("question"), "task.question", 4096),
        requirements=tuple(_requirement(item) for item in raw_requirements),
    )
    validate_task_spec(task)
    return task


def validate_task_spec(task: TaskSpec) -> None:
    _bounded(task.question, "task.question", 4096)
    if not 1 <= len(task.requirements) <= 10:
        raise ValueError("task must declare between one and ten requirements")
    actual = [item.id for item in task.requirements]
    expected = [f"E{index}" for index in range(1, len(actual) + 1)]
    if len(set(actual)) != len(actual):
        raise ValueError("requirement IDs must be unique")
    if actual != expected:
        raise ValueError("requirement IDs must be sequential from E1")
    for item in task.requirements:
        _bounded(item.subject, "requirement.subject", 512)
        _bounded(item.property, "requirement.property", 512)
        _bounded(item.temporal_scope, "requirement.temporal_scope", 256)
        _bounded(item.expected_value_type, "requirement.expected_value_type", 128)


def _corpus_record(value: Any) -> CorpusRecord:
    item = _mapping(value, "corpus record")
    raw_support = item.get("supports_requirements", [])
    if not isinstance(raw_support, list):
        raise ValueError("supports_requirements must be an array")
    support = tuple(
        _bounded(ref, "supports_requirements item", 32) for ref in raw_support
    )
    if len(set(support)) != len(support):
        raise ValueError("supports_requirements values must be unique")
    return CorpusRecord(
        record_id=_bounded(item.get("record_id"), "record_id", 256),
        text=_bounded(item.get("text"), "text", 16384),
        subject=_bounded(item.get("subject"), "subject", 512),
        property=_bounded(item.get("property"), "property", 512),
        valid_time=_bounded(item.get("valid_time"), "valid_time", 256),
        source_time=_bounded(item.get("source_time"), "source_time", 256),
        attributes=_frozen_mapping(item.get("attributes", {}), "attributes"),
        supports_requirements=support,
    )


def load_corpus_records(
    source: str | Path | Iterable[Mapping[str, Any]],
) -> tuple[CorpusRecord, ...]:
    if isinstance(source, (str, Path)):
        lines = Path(source).read_text(encoding="utf-8").splitlines()
        values = [json.loads(line) for line in lines if line.strip()]
    else:
        values = list(source)
    records = tuple(_corpus_record(item) for item in values)
    ids = [record.record_id for record in records]
    if len(set(ids)) != len(ids):
        raise ValueError("corpus record IDs must be unique")
    return records


def _evidence_record(value: Any) -> EvidenceRecord:
    item = _mapping(value, "evidence record")
    raw_support = item.get("supports_requirements")
    if not isinstance(raw_support, list) or not raw_support:
        raise ValueError("evidence record must support at least one requirement")
    support = tuple(
        _bounded(ref, "supports_requirements item", 32) for ref in raw_support
    )
    if len(set(support)) != len(support):
        raise ValueError("supports_requirements values must be unique")
    return EvidenceRecord(
        evidence_id=_bounded(item.get("evidence_id"), "evidence_id", 256),
        text=_bounded(item.get("text"), "evidence text", 16384),
        supports_requirements=support,
        metadata=_frozen_mapping(item.get("metadata", {}), "metadata"),
    )


def load_evidence_pack(source: str | Path | Mapping[str, Any]) -> EvidencePack:
    value = _load_object(source, "evidence pack")
    raw_requirements = value.get("requirements")
    raw_records = value.get("records")
    if not isinstance(raw_requirements, list) or not isinstance(raw_records, list):
        raise ValueError("evidence pack requirements and records must be arrays")
    pack = EvidencePack(
        requirements=tuple(
            _bounded(ref, "evidence pack requirement", 32)
            for ref in raw_requirements
        ),
        records=tuple(_evidence_record(item) for item in raw_records),
    )
    validate_evidence_pack(pack)
    return pack


def validate_evidence_pack(pack: EvidencePack, task: TaskSpec | None = None) -> None:
    if not 1 <= len(pack.requirements) <= 10:
        raise ValueError("evidence pack must declare between one and ten requirements")
    expected = tuple(f"E{index}" for index in range(1, len(pack.requirements) + 1))
    if pack.requirements != expected:
        raise ValueError("evidence pack requirements must be unique and sequential")
    if task is not None and pack.requirements != tuple(
        item.id for item in task.requirements
    ):
        raise ValueError("evidence pack requirements do not match the task")
    evidence_ids = [record.evidence_id for record in pack.records]
    if len(set(evidence_ids)) != len(evidence_ids):
        raise ValueError("evidence IDs must be unique")
    declared = set(pack.requirements)
    for record in pack.records:
        unknown = set(record.supports_requirements) - declared
        if unknown:
            raise ValueError("evidence record references an unknown requirement")


def _answer_component(value: Any) -> AnswerComponent:
    item = _mapping(value, "answer component")
    raw_evidence = item.get("evidence_ids")
    if not isinstance(raw_evidence, list):
        raise ValueError("answer component evidence_ids must be an array")
    evidence_ids = tuple(
        _bounded(ref, "answer evidence ID", 256) for ref in raw_evidence
    )
    if len(set(evidence_ids)) != len(evidence_ids):
        raise ValueError("answer evidence IDs must be unique")
    status = _bounded(item.get("status"), "answer status", 64)
    if status not in _STATUSES:
        raise ValueError("answer status is not recognized")
    note = item.get("note", "")
    if not isinstance(note, str) or len(note) > 2048:
        raise ValueError("answer note must be a bounded string")
    return AnswerComponent(
        requirement_id=_bounded(item.get("requirement_id"), "requirement_id", 32),
        status=status,
        value=_scalar(item.get("value"), "answer value"),
        evidence_ids=evidence_ids,
        note=note,
    )


def load_answer_contract(source: str | Path | Mapping[str, Any]) -> AnswerContract:
    value = _load_object(source, "answer contract")
    raw_components = value.get("components")
    if not isinstance(raw_components, list):
        raise ValueError("answer components must be an array")
    answer = AnswerContract(
        components=tuple(_answer_component(item) for item in raw_components),
        overall_status=_bounded(value.get("overall_status"), "overall_status", 64),
    )
    validate_answer_contract(answer)
    return answer


def validate_answer_contract(
    answer: AnswerContract,
    task: TaskSpec | None = None,
    evidence_pack: EvidencePack | None = None,
) -> None:
    if answer.overall_status not in _STATUSES:
        raise ValueError("overall answer status is not recognized")
    if not 1 <= len(answer.components) <= 10:
        raise ValueError("answer must contain between one and ten components")
    requirement_ids = [item.requirement_id for item in answer.components]
    if len(set(requirement_ids)) != len(requirement_ids):
        raise ValueError("answer requirement IDs must be unique")
    if task is not None:
        declared = {item.id for item in task.requirements}
        if set(requirement_ids) - declared:
            raise ValueError("answer references an unknown requirement")
    evidence_by_id: dict[str, EvidenceRecord] = {}
    if evidence_pack is not None:
        evidence_by_id = {record.evidence_id: record for record in evidence_pack.records}
    for component in answer.components:
        if component.status == "supported" and not component.evidence_ids:
            raise ValueError("supported answer components require evidence")
        if evidence_pack is None:
            continue
        for evidence_id in component.evidence_ids:
            if evidence_id not in evidence_by_id:
                raise ValueError("answer references an unknown evidence ID")
            if component.requirement_id not in evidence_by_id[evidence_id].supports_requirements:
                raise ValueError("cited evidence does not support the answer requirement")
