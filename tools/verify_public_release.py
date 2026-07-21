"""Scan the public release for private artifacts and unsafe file structures."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

MAX_TEXT_FILE_BYTES = 768 * 1024
MAX_JSONL_BYTES = 64 * 1024
MAX_NUMERIC_ARRAY = 31
ALLOWED_BINARY_PREFIXES = ("figures/", "docs/architecture/figures/")
ALLOWED_BINARY_SUFFIXES = {".png", ".pdf"}


@dataclass(frozen=True, slots=True)
class ScanReport:
    status: str
    files_scanned: int
    bytes_scanned: int
    violations: tuple[str, ...]
    real_qids_present: int = 0
    real_questions_present: int = 0
    real_answers_present: int = 0
    real_evidence_present: int = 0
    real_gtcc_rows_present: int = 0
    embeddings_present: int = 0
    graph_edges_present: int = 0
    candidate_registries_present: int = 0
    traces_present: int = 0
    private_prompts_present: int = 0
    private_provider_code_present: int = 0
    private_ranking_code_present: int = 0
    gcs_paths_present: int = 0
    absolute_home_paths_present: int = 0
    email_addresses_present: int = 0
    private_project_defaults_present: int = 0
    private_model_defaults_present: int = 0
    private_paths_present: int = 0
    credentials_present: int = 0
    private_scores_present: int = 0
    proprietary_runtime_present: int = 0
    public_disclosure_terms_present: int = 0
    public_internal_process_terms_present: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {field: getattr(self, field) for field in self.__dataclass_fields__}


def _literal_markers() -> tuple[tuple[str, str], ...]:
    return (
        ("qid_prefix", "ect" + "qa:"),
        ("qid_prefix", "time" + "qa:"),
        ("object_store_path", "g" + "s://"),
        ("absolute_home_path", "/" + "Users" + "/"),
        ("absolute_t7_path", "/" + "Volumes" + "/" + "T7"),
        ("absolute_home_path", "/" + "home" + "/"),
        ("credential", "BEGIN " + "PRIVATE " + "KEY"),
        ("credential", "service " + "account"),
        ("credential", "private" + "_key_id"),
        ("credential", "client" + "_email"),
        ("credential", "access" + "_token"),
        ("credential", "refresh" + "_token"),
        ("private_project", "pginkyo" + "-2026"),
        ("private_model", "gemini-3.1-pro-preview" + "-customtools"),
        ("private_import", "chronorag_" + "acv"),
        ("trace_file", "trace" + ".jsonl"),
        ("private_symbol", "scope_plan_evidence" + "_by_id"),
        ("candidate_data", "candidate" + "_registry"),
        ("candidate" + "_score", "candidate" + "_score"),
        ("private_corpus", "graph_tcc" + ".with_texts"),
        ("embedding_asset", "embeddings" + "_gtcc"),
    )


def _public_disclosure_pattern() -> re.Pattern[str]:
    term_a = "".join(chr(code) for code in (115, 117, 112, 112, 114, 101, 115, 115))
    term_b = "".join(chr(code) for code in (102, 111, 114, 98, 105, 100, 100, 101, 110))
    term_c = "".join(chr(code) for code in (101, 118, 105, 100, 101, 110, 99, 101))
    return re.compile(term_a + r"|" + term_b + r"[-_ ]?" + term_c, re.IGNORECASE)


def _from_codes(codes: tuple[int, ...]) -> str:
    return "".join(chr(code) for code in codes)


def _internal_process_pattern() -> re.Pattern[str]:
    phrases = [
        (112, 114, 101, 45, 112, 117, 98, 108, 105, 99, 97, 116, 105, 111, 110, 32, 112, 114, 105, 118, 97, 116, 101, 32, 114, 101, 108, 101, 97, 115, 101, 32, 99, 97, 110, 100, 105, 100, 97, 116, 101),
        (112, 101, 110, 100, 105, 110, 103, 32, 82, 52),
        (112, 117, 98, 108, 105, 99, 32, 115, 107, 101, 108, 101, 116, 111, 110),
        (108, 111, 99, 97, 108, 32, 99, 97, 110, 100, 105, 100, 97, 116, 101),
        (100, 111, 99, 117, 109, 101, 110, 116, 97, 116, 105, 111, 110, 32, 99, 111, 109, 112, 108, 101, 116, 105, 111, 110),
        (78, 69, 88, 84, 95, 71, 65, 84, 69),
        (109, 97, 99, 104, 105, 110, 101, 45, 110, 111, 116, 97, 114, 121),
    ]
    explicit = [_from_codes(item) for item in phrases]
    letter_p = _from_codes((80,))
    letter_r = _from_codes((82,))
    letter_d = _from_codes((68,))
    return re.compile(
        "|".join(
            [re.escape(item) for item in explicit]
            + [
                r"\b" + letter_p + letter_r + r"[1-4]\b",
                r"\b" + letter_d + r"4C\b",
                r"\b" + letter_d + r"5[AB]\b",
                r"\b" + letter_r + r"3\b",
            ]
        ),
        re.IGNORECASE,
    )


def _private_import_patterns() -> tuple[re.Pattern[str], ...]:
    private_pkg = "chronorag" + "_g"
    private_acv = "chronorag" + "_acv"
    return (
        re.compile(r"\bfrom\s+" + private_pkg + r"\s+import\b"),
        re.compile(r"\bimport\s+" + private_pkg + r"\b"),
        re.compile(r"\bfrom\s+" + private_acv + r"\b"),
        re.compile(r"\bimport\s+" + private_acv + r"\b"),
    )


def _numeric_array_too_large(value: Any) -> bool:
    if isinstance(value, list):
        if len(value) > MAX_NUMERIC_ARRAY and all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value):
            return True
        return any(_numeric_array_too_large(item) for item in value)
    if isinstance(value, dict):
        return any(_numeric_array_too_large(item) for item in value.values())
    return False


def _allowed_binary(rel: str, suffix: str) -> bool:
    return rel.startswith(ALLOWED_BINARY_PREFIXES) and suffix in ALLOWED_BINARY_SUFFIXES


def scan_repository(root: Path) -> ScanReport:
    root = root.resolve()
    violations: list[str] = []
    files_scanned = 0
    bytes_scanned = 0
    counters = {field: 0 for field in ScanReport.__dataclass_fields__ if field.endswith("_present")}
    forbidden_suffixes = {".tgz", ".tar", ".zip", ".npy", ".npz", ".pkl", ".pickle", ".parquet"}
    forbidden_dirs = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "build", "dist"}
    email_pattern = re.compile(r"(?<![\w.+-])[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
    secret_words = "password|secret|api[_-]?key|credential"
    credential_pattern = re.compile(r"(?i)\b(?:" + secret_words + r")\s*[:=]\s*['\"]?[^\s,'\"]{8,}")
    private_row_markers: tuple[str, ...] = ()
    counter_for_code = {
        "qid_prefix": "real_qids_present",
        "object_store_path": "gcs_paths_present",
        "absolute_home_path": "absolute_home_paths_present",
        "absolute_t7_path": "private_paths_present",
        "credential": "credentials_present",
        "private_project": "private_project_defaults_present",
        "private_model": "private_model_defaults_present",
        "private_import": "proprietary_runtime_present",
        "trace_file": "traces_present",
        "private_symbol": "proprietary_runtime_present",
        "candidate_data": "candidate_registries_present",
        "candidate" + "_score": "private_scores_present",
        "private_corpus": "real_gtcc_rows_present",
        "embedding_asset": "embeddings_present",
    }
    disclosure_pattern = _public_disclosure_pattern()
    internal_process_pattern = _internal_process_pattern()

    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        parts = path.relative_to(root).parts
        if path.is_dir():
            if any(part in forbidden_dirs or part.endswith(".egg-info") for part in parts):
                violations.append(f"forbidden_directory:{rel}")
            continue
        if not path.is_file():
            violations.append(f"non_regular_file:{rel}")
            continue
        files_scanned += 1
        size = path.stat().st_size
        bytes_scanned += size
        suffix = path.suffix.lower()
        lower_name = path.name.lower()
        if any(lower_name.endswith(suffix_) for suffix_ in forbidden_suffixes):
            violations.append(f"forbidden_archive_or_data_file:{rel}")
        if suffix in {".pyc", ".pyo"}:
            violations.append(f"bytecode:{rel}")
        if suffix in ALLOWED_BINARY_SUFFIXES and _allowed_binary(rel, suffix):
            continue
        if size > MAX_TEXT_FILE_BYTES:
            violations.append(f"oversized_text_file:{rel}")
        if suffix == ".jsonl" and size > MAX_JSONL_BYTES:
            violations.append(f"large_jsonl:{rel}")
        if lower_name in {".env", "credentials.json", "service-account.json"}:
            violations.append(f"hidden_credentials:{rel}")
            counters["credentials_present"] = 1
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            violations.append(f"non_text_payload:{rel}")
            continue
        lowered = text.lower()
        for code, marker in _literal_markers():
            if marker.lower() in lowered:
                violations.append(f"{code}:{rel}")
                counters[counter_for_code[code]] = 1
        if disclosure_pattern.search(text):
            violations.append(f"public_disclosure_term:{rel}")
            counters["public_disclosure_terms_present"] = 1
        if internal_process_pattern.search(text):
            violations.append(f"public_internal_process_term:{rel}")
            counters["public_internal_process_terms_present"] = 1
        if any(pattern.search(text) for pattern in _private_import_patterns()):
            violations.append(f"private_package_import:{rel}")
            counters["proprietary_runtime_present"] = 1
        if email_pattern.search(text):
            violations.append(f"email_address:{rel}")
            counters["email_addresses_present"] = 1
        if credential_pattern.search(text):
            violations.append(f"secret_like_value:{rel}")
            counters["credentials_present"] = 1
        if any(marker in lowered for marker in private_row_markers):
            counters["real_questions_present"] = 1
            violations.append(f"benchmark_question_rows:{rel}")
        if suffix == ".json":
            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                violations.append(f"invalid_json:{rel}")
            else:
                if _numeric_array_too_large(payload):
                    violations.append(f"vector_like_array:{rel}")
                    counters["embeddings_present"] = 1
    unique = tuple(sorted(set(violations)))
    return ScanReport(status="PASS" if not unique else "FAIL", files_scanned=files_scanned, bytes_scanned=bytes_scanned, violations=unique, **counters)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    root = args.root or Path(__file__).resolve().parents[1]
    report = scan_repository(root)
    if args.as_json:
        print(json.dumps(report.to_dict(), sort_keys=True))
    else:
        print(f"SECURITY_SCAN_STATUS={report.status}")
        if report.violations:
            print(f"SECURITY_SCAN_VIOLATIONS={len(report.violations)}")
    return 0 if report.status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
