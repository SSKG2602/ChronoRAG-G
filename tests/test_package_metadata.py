from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_package_metadata_is_standards_compliant():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]

    assert project["license"] == "Apache-2.0"
    assert project["license-files"] == ["LICENSE"]
    assert not any(item.startswith("License ::") for item in project["classifiers"])
    assert project["version"] == "0.4.0rc1"
    assert project["name"] == "chronorag-g-public"
