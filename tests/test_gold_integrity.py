import json
from pathlib import Path

GOLD_DIR = Path(__file__).resolve().parent.parent / "tests" / "gold"


def _load(name: str) -> dict:
    return json.loads((GOLD_DIR / name).read_text())


def test_gold_large_is_well_formed():
    data = _load("eval_gold_large.json")
    assert data["docs"] and data["queries"]
    doc_ids = {d["id"] for d in data["docs"]}
    for q in data["queries"]:
        assert q["query"]
        assert q["relevant"], q["id"]
        for rel in q["relevant"]:
            assert rel in doc_ids, f"{q['id']} references missing doc {rel}"


def test_gold_semantic_is_well_formed():
    data = _load("eval_gold_semantic.json")
    doc_ids = {d["id"] for d in data["docs"]}
    for q in data["queries"]:
        for rel in q["relevant"]:
            assert rel in doc_ids, f"{q['id']} references missing doc {rel}"
