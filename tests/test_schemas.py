import importlib.util
import json
from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
SCHEMA_NAMES = [
    "task-spec.schema.json",
    "gtcc.schema.json",
    "evidence-pack.schema.json",
    "answer-contract.schema.json",
]


@pytest.mark.parametrize("name", SCHEMA_NAMES)
def test_schema_is_draft_2020_12_and_has_required_fields(name):
    schema = json.loads((SCHEMAS / name).read_text())
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["type"] == "object"
    assert schema["required"]


def test_task_schema_excludes_forbidden_production_fields():
    schema = json.loads((SCHEMAS / "task-spec.schema.json").read_text())
    text = json.dumps(schema).lower()
    for field in ("answer", "gold", "provider", "model"):
        assert f'"{field}"' not in text


def test_schemas_have_no_local_paths_or_private_defaults():
    text = "\n".join((SCHEMAS / name).read_text() for name in SCHEMA_NAMES)
    assert not re.search(r"/(?:Users|home)/", text)
    private_defaults = ["pginkyo" + "-2026", "gemini-3.1" + "-pro-preview-customtools"]
    assert not any(value in text for value in private_defaults)


@pytest.mark.skipif(importlib.util.find_spec("jsonschema") is None, reason="optional validator unavailable")
def test_synthetic_examples_validate_with_optional_jsonschema():
    import jsonschema

    example = ROOT / "examples/synthetic"
    task_schema = json.loads((SCHEMAS / "task-spec.schema.json").read_text())
    corpus_schema = json.loads((SCHEMAS / "gtcc.schema.json").read_text())
    evidence_schema = json.loads((SCHEMAS / "evidence-pack.schema.json").read_text())
    answer_schema = json.loads((SCHEMAS / "answer-contract.schema.json").read_text())
    jsonschema.validate(json.loads((example / "task.json").read_text()), task_schema)
    for line in (example / "corpus.jsonl").read_text().splitlines():
        jsonschema.validate(json.loads(line), corpus_schema)
    jsonschema.validate(json.loads((example / "evidence-pack.json").read_text()), evidence_schema)
    jsonschema.validate(json.loads((example / "answer.json").read_text()), answer_schema)
