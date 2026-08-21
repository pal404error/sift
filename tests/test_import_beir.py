import importlib.util
from pathlib import Path


def _load_import_beir():
    p = Path(__file__).resolve().parent.parent / "scripts" / "import_beir.py"
    spec = importlib.util.spec_from_file_location("import_beir", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_build_gold_keeps_relevant_docs_and_adds_distractors():
    mod = _load_import_beir()
    corpus = {
        "d1": {"title": "A", "text": "alpha"},
        "d2": {"title": "B", "text": "beta"},
        "d3": {"title": "C", "text": "gamma"},
        "d4": {"title": "D", "text": "delta"},
    }
    queries = {"q1": "find alpha", "q2": "find beta"}
    qrels = {"q1": {"d1": 1}, "q2": {"d2": 1}}

    gold = mod.build_gold(corpus, queries, qrels, name="tiny", sample=10, max_docs=3, seed=1)

    doc_ids = {d["id"] for d in gold["docs"]}
    assert {"d1", "d2"} <= doc_ids  # all relevant docs retained
    assert len(gold["docs"]) == 3    # capped at max_docs (2 relevant + 1 distractor)
    assert len(gold["queries"]) == 2
    for q in gold["queries"]:
        assert q["relevant"]  # every query has at least one relevant doc present


def test_build_gold_skips_unrated_queries():
    mod = _load_import_beir()
    corpus = {"d1": {"text": "x"}, "d2": {"text": "y"}}
    queries = {"q1": "a", "q2": "b"}
    qrels = {"q1": {"d1": 1}, "q2": {}}  # q2 has no relevant docs
    gold = mod.build_gold(corpus, queries, qrels, sample=10, max_docs=10)
    assert [q["id"] for q in gold["queries"]] == ["q1"]
