#!/usr/bin/env python3
import json, math
from pathlib import Path
base = Path(__file__).parent
task = json.loads((base / "task.json").read_text())
pack = json.loads((base / "evidence_pack.json").read_text())
result = json.loads((base / "result.json").read_text())
rows = [json.loads(x) for x in (base / "corpus.jsonl").read_text().splitlines() if x.strip()]

def norm(v):
    return math.sqrt(sum(x * x for x in v))

def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / (norm(a) * norm(b))

assert task["candidate_budget"]["expansion_triggered"] is False
assert abs(sum(pack["weights"].values()) - 1.0) < 1e-9
seen = {}
for row in rows:
    seen.setdefault(row["evidence_id"], row)
assert set(seen) == set(result["A"]["columns"]) == set(result["Y"]["columns"])
computed = {}
for req in task["requirements"]:
    slot = req["slot_id"]
    qv = pack["query_vectors"][slot]
    ordered = []
    for evidence_id, row in seen.items():
        entity = int(row["entity"] == req["entity"])
        prop = int(any(c["property"] == req["property"] for c in row["claims"]))
        temporal = int(row["interval"] == req["interval"])
        projection = (.35 * entity) + (.35 * prop) + (.20 * temporal) + .10
        key = (1 - projection, -cos(qv, row["vector"]), evidence_id)
        ordered.append((key, row["candidate_id"], evidence_id))
    ordered.sort()
    best = ordered[0]
    assert pack["selected"][slot] == best[1]
    if len(ordered) > 1 and ordered[0][0] == ordered[1][0]:
        assert ordered[0][2] < ordered[1][2]
    computed[slot] = best[2]
cols = result["A"]["columns"]
col_index = {c: i for i, c in enumerate(cols)}
for slot_i, req in enumerate(task["requirements"]):
    refs = result["answer_evidence_refs"][req["slot_id"]]
    assert refs and all(r in col_index for r in refs)
    for ref in refs:
        assert result["A"]["values"][slot_i][col_index[ref]] == 1
for j, col in enumerate(cols):
    included = any(row[j] == 1 for row in result["A"]["values"])
    assert result["Y"]["values"][j] == int(included)
used = sum(pack["per_record_costs"][c] * result["Y"]["values"][j] for j, c in enumerate(cols))
assert used == result["budget_used"] == 5 <= pack["budget_B"]
assert computed == {"E1": "p1", "E2": "p1"}
assert result["strict_coverage"] == "2/2"
assert result["micro_coverage"] == "2/2"
print("SYNTHETIC_CASE_VALIDATION=PASS")
