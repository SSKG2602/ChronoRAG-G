"""Public-safe ChronoRAG-G interfaces, contracts, and deterministic metrics."""

from .assembler import assemble_slot_preserving_answer, render_enumeration
from .contracts import (
    AnswerComponent,
    AnswerContract,
    CorpusRecord,
    EvidencePack,
    EvidenceRecord,
    EvidenceRequirement,
    TaskSpec,
    load_answer_contract,
    load_corpus_records,
    load_evidence_pack,
    load_task_spec,
    validate_answer_contract,
    validate_evidence_pack,
    validate_task_spec,
)
from .metrics import (
    MetricResult,
    answer_accuracy,
    format_percentage,
    hybrid_evidence_resolution,
    hybrid_success,
    micro_slot_resolution,
    strict_slot_resolution,
)
from .registry import EvidenceRegistry
from .results import PUBLIC_METRICS, assert_public_metrics, percent
from .schemas import (
    AssembledAnswer,
    EvidenceCandidate,
    EvidenceObligation,
    SlotAllocation,
    TemporalRecord,
)
from .validators import TRACE_STEPS, validate_obligations, validate_record, validate_trace_steps

__all__ = [
    "AnswerComponent",
    "AnswerContract",
    "AssembledAnswer",
    "CorpusRecord",
    "EvidenceCandidate",
    "EvidenceObligation",
    "EvidencePack",
    "EvidenceRecord",
    "EvidenceRegistry",
    "EvidenceRequirement",
    "MetricResult",
    "PUBLIC_METRICS",
    "SlotAllocation",
    "TaskSpec",
    "TemporalRecord",
    "TRACE_STEPS",
    "answer_accuracy",
    "assemble_slot_preserving_answer",
    "assert_public_metrics",
    "format_percentage",
    "hybrid_evidence_resolution",
    "hybrid_success",
    "load_answer_contract",
    "load_corpus_records",
    "load_evidence_pack",
    "load_task_spec",
    "micro_slot_resolution",
    "percent",
    "render_enumeration",
    "strict_slot_resolution",
    "validate_answer_contract",
    "validate_evidence_pack",
    "validate_obligations",
    "validate_record",
    "validate_task_spec",
    "validate_trace_steps",
]

__version__ = "0.4.0rc1"
