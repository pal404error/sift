"""Validate that CI/CD workflow YAML and the Makefile are well-formed.

These are config files that drive the quality gates, so they must parse even though
we cannot run GitHub Actions locally. Keeps the pipeline itself under test.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"


def _yaml_docs(path: Path) -> list:
    import yaml

    text = path.read_text()
    return list(yaml.safe_load_all(text))


def test_ci_workflow_parses():
    data = _yaml_docs(WORKFLOWS / "ci.yml")
    doc = data[0]
    assert doc["name"] == "CI"
    assert "jobs" in doc
    assert {"quality", "security", "docker"} <= set(doc["jobs"])


def test_release_workflow_parses():
    data = _yaml_docs(WORKFLOWS / "release.yml")
    doc = data[0]
    assert doc["name"] == "Release"
    # YAML 1.1 parses the `on:` key as boolean True.
    on = doc.get("on", doc.get(True, {}))
    assert on["push"]["tags"] == ["v*"]
    assert "docker-release" in doc["jobs"]


def test_makefile_has_ci_targets():
    makefile = ROOT / "Makefile"
    text = makefile.read_text()
    for target in ("install", "lint", "type", "test", "cov", "audit", "ci", "docker"):
        assert f"{target}:" in text, f"missing Makefile target {target}"
