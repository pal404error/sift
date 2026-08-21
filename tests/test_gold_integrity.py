import json
from pathlib import Path

GOLD_DIR = Path(__file__).resolve().parent.parent / "tests" / "gold"


def _validate(path: Path) -> None:
    data = json.loads(path.read_text())
    assert data["docs"] and data["queries"], path.name
    doc_ids = {d["id"] for d in data["docs"]}
    for q in data["queries"]:
        assert q["query"], q.get("id")
        assert q["relevant"], q.get("id")
        for rel in q["relevant"]:
            assert rel in doc_ids, f"{q.get('id')} -> missing {rel}"


def test_all_gold_files_are_well_formed():
    # Scans every gold JSON present (authored + any regenerated BEIR file).
    for path in sorted(GOLD_DIR.glob("eval_gold_*.json")):
        _validate(path)
