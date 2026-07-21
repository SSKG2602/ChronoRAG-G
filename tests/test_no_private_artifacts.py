import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("public_release_scanner", ROOT / "tools/verify_public_release.py")
SCANNER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = SCANNER
SPEC.loader.exec_module(SCANNER)


def test_repository_has_no_private_artifacts():
    report = SCANNER.scan_repository(ROOT)
    assert report.status == "PASS", report.violations
    zero_fields = [
        name for name in report.__dataclass_fields__
        if name.endswith("_present")
    ]
    assert all(getattr(report, name) == 0 for name in zero_fields)


def test_scanner_rejects_private_marker(tmp_path):
    (tmp_path / "unsafe.txt").write_text("g" + "s://private-bucket/object")
    assert SCANNER.scan_repository(tmp_path).status == "FAIL"


def test_scanner_rejects_archive(tmp_path):
    (tmp_path / "payload.zip").write_text("not an archive")
    assert SCANNER.scan_repository(tmp_path).status == "FAIL"


def test_scanner_rejects_large_numeric_array(tmp_path):
    values = ",".join(str(index) for index in range(40))
    (tmp_path / "values.json").write_text("[" + values + "]")
    assert SCANNER.scan_repository(tmp_path).status == "FAIL"


def test_scanner_rejects_cache_directory(tmp_path):
    cache = tmp_path / ("__py" + "cache__")
    cache.mkdir()
    (cache / "item.pyc").write_bytes(b"bytecode")
    assert SCANNER.scan_repository(tmp_path).status == "FAIL"


def test_scanner_rejects_email_address(tmp_path):
    address = "person" + "@" + "example.com"
    (tmp_path / "contact.txt").write_text(address)
    assert SCANNER.scan_repository(tmp_path).status == "FAIL"


def test_scanner_rejects_public_disclosure_marker(tmp_path):
    marker = "".join(chr(code) for code in (115, 117, 112, 112, 114, 101, 115, 115))
    (tmp_path / "marker.txt").write_text(marker)
    assert SCANNER.scan_repository(tmp_path).status == "FAIL"


def test_scanner_rejects_split_public_disclosure_marker(tmp_path):
    left = "".join(chr(code) for code in (102, 111, 114, 98, 105, 100, 100, 101, 110))
    right = "".join(chr(code) for code in (101, 118, 105, 100, 101, 110, 99, 101))
    (tmp_path / "marker.txt").write_text(left + "-" + right)
    assert SCANNER.scan_repository(tmp_path).status == "FAIL"


def test_scanner_rejects_internal_process_marker(tmp_path):
    marker = "".join(chr(code) for code in (80, 82, 52))
    (tmp_path / "marker.txt").write_text(marker)
    assert SCANNER.scan_repository(tmp_path).status == "FAIL"
