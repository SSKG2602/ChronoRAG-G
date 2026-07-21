"""Run the deterministic, contracts-only synthetic demonstration."""

from __future__ import annotations

import json
from pathlib import Path
import sys

EXAMPLE_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = EXAMPLE_DIR.parents[1]
SOURCE_DIR = REPOSITORY_ROOT / "src"
if SOURCE_DIR.is_dir():
    sys.path.insert(0, str(SOURCE_DIR))

from chronorag_public import (  # noqa: E402
    load_answer_contract,
    load_corpus_records,
    load_evidence_pack,
    load_task_spec,
    strict_slot_resolution,
    validate_answer_contract,
    validate_evidence_pack,
    validate_task_spec,
)


def main() -> int:
    task = load_task_spec(EXAMPLE_DIR / "task.json")
    corpus = load_corpus_records(EXAMPLE_DIR / "corpus.jsonl")
    evidence_pack = load_evidence_pack(EXAMPLE_DIR / "evidence-pack.json")
    answer = load_answer_contract(EXAMPLE_DIR / "answer.json")

    validate_task_spec(task)
    validate_evidence_pack(evidence_pack, task)
    validate_answer_contract(answer, task, evidence_pack)

    shared = next(
        record
        for record in evidence_pack.records
        if len(record.supports_requirements) == 2
    )
    resolved = all(component.status == "supported" for component in answer.components)
    metric = strict_slot_resolution(int(resolved), 1)
    actual = {
        "requirements": len(task.requirements),
        "corpus_records": len(corpus),
        "shared_support": list(shared.supports_requirements),
        "strict_slot_metric": metric.as_dict(),
    }
    expected = json.loads((EXAMPLE_DIR / "expected.json").read_text(encoding="utf-8"))
    if actual != expected:
        raise AssertionError("synthetic result differs from the expected artifact")
    print("PUBLIC_SYNTHETIC_DEMO_SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
