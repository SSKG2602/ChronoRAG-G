from copy import deepcopy

import pytest

from chronorag_public import (
    load_answer_contract,
    load_corpus_records,
    load_evidence_pack,
    load_task_spec,
    validate_answer_contract,
    validate_evidence_pack,
)


def requirement(identifier="E1", subject="Acme Holdings", property_name="service margin"):
    return {
        "id": identifier,
        "subject": subject,
        "property": property_name,
        "temporal_scope": "2031-Q1",
        "expected_value_type": "percentage",
        "optional_qualifiers": {"unit": "percent"},
    }


def task_mapping(requirements=None):
    return {"question": "What invented values are reported?", "requirements": requirements or [requirement()]}


def pack_mapping(support=None):
    return {
        "requirements": ["E1"],
        "records": [{
            "evidence_id": "EV1",
            "text": "An invented value is stated.",
            "supports_requirements": support or ["E1"],
            "metadata": {"synthetic": True},
        }],
    }


def answer_mapping(evidence_ids=None, status="supported", requirement_id="E1"):
    return {
        "components": [{
            "requirement_id": requirement_id,
            "status": status,
            "value": "17 percent" if status == "supported" else None,
            "evidence_ids": ["EV1"] if evidence_ids is None else evidence_ids,
            "note": "Invented example.",
        }],
        "overall_status": status,
    }


def test_valid_task():
    task = load_task_spec(task_mapping())
    assert task.requirements[0].id == "E1"


def test_nonsequential_ids_rejected():
    with pytest.raises(ValueError, match="sequential"):
        load_task_spec(task_mapping([requirement("E2")]))


def test_duplicate_ids_rejected():
    with pytest.raises(ValueError, match="unique"):
        load_task_spec(task_mapping([requirement("E1"), requirement("E1")]))


@pytest.mark.parametrize("field", ["subject", "property"])
def test_empty_required_fields_rejected(field):
    item = requirement()
    item[field] = ""
    with pytest.raises(ValueError, match=field):
        load_task_spec(task_mapping([item]))


def test_more_than_ten_requirements_rejected():
    items = [requirement(f"E{index}") for index in range(1, 12)]
    with pytest.raises(ValueError, match="one and ten"):
        load_task_spec(task_mapping(items))


def test_unknown_requirement_reference_rejected():
    raw = pack_mapping(["E2"])
    with pytest.raises(ValueError, match="unknown requirement"):
        load_evidence_pack(raw)


def test_unknown_evidence_id_rejected():
    task = load_task_spec(task_mapping())
    pack = load_evidence_pack(pack_mapping())
    answer = load_answer_contract(answer_mapping(["EV-MISSING"]))
    with pytest.raises(ValueError, match="unknown evidence"):
        validate_answer_contract(answer, task, pack)


def test_supported_answer_requires_evidence():
    with pytest.raises(ValueError, match="require evidence"):
        load_answer_contract(answer_mapping([]))


def test_unsupported_answer_may_omit_evidence():
    answer = load_answer_contract(answer_mapping([], status="unsupported"))
    assert answer.components[0].evidence_ids == ()


def test_one_record_supports_multiple_requirements():
    task = load_task_spec(task_mapping([
        requirement("E1"),
        requirement("E2", "Beta Systems", "subscription retention"),
    ]))
    raw = pack_mapping(["E1", "E2"])
    raw["requirements"] = ["E1", "E2"]
    pack = load_evidence_pack(raw)
    validate_evidence_pack(pack, task)
    assert pack.records[0].supports_requirements == ("E1", "E2")


def test_duplicate_corpus_ids_rejected():
    record = {
        "record_id": "R1", "text": "Invented text.", "subject": "Orchid Energy",
        "property": "operating yield", "valid_time": "2031", "source_time": "2032",
        "attributes": {},
    }
    with pytest.raises(ValueError, match="unique"):
        load_corpus_records([record, dict(record)])


def test_deterministic_serialization():
    first = task_mapping()
    first["requirements"][0]["optional_qualifiers"] = {"zeta": 2, "alpha": 1}
    second = deepcopy(first)
    second["requirements"][0]["optional_qualifiers"] = {"alpha": 1, "zeta": 2}
    assert load_task_spec(first).to_json() == load_task_spec(second).to_json()


def test_input_mappings_are_not_mutated():
    raw_task = task_mapping()
    raw_pack = pack_mapping()
    raw_answer = answer_mapping()
    before = deepcopy((raw_task, raw_pack, raw_answer))
    load_task_spec(raw_task)
    load_evidence_pack(raw_pack)
    load_answer_contract(raw_answer)
    assert (raw_task, raw_pack, raw_answer) == before
