from __future__ import annotations

from llm_search.engine import SearchEngine
from llm_search.lexical_index import LexicalIndex
from llm_search.providers import FakeEmbedding, FakeLLM
from llm_search.store import InMemoryStore


def _hybrid_engine() -> SearchEngine:
    return SearchEngine(
        store=InMemoryStore(),
        embedding=FakeEmbedding(dim=32),
        llm=FakeLLM(),
        lexical=LexicalIndex(),
    )


def test_lexical_index_ranks_matching_doc_first():
    idx = LexicalIndex()
    idx.add("a", "the quick brown fox")
    idx.add("b", "lazy dog sleeps")
    hits = idx.search("quick brown fox", top_n=5)
    assert hits and hits[0][0] == "a"


def test_lexical_index_idf_downweights_common_terms():
    idx = LexicalIndex()
    idx.add("rare", "kubernetes operator pattern")
    idx.add("common", "kubernetes and the of")
    hits = dict(idx.search("kubernetes operator pattern", top_n=5))
    assert "common" in hits
    assert hits["rare"] > hits["common"]


def test_hybrid_surfaces_lexical_only_match():
    eng = _hybrid_engine()
    eng.lexical.add(  # only in the lexical index, not the vector store
        "lx1",
        "kubernetes operator pattern",
        {"doc_url": "u", "doc_title": "t", "index": 0, "text": "kubernetes operator pattern"},
    )
    res = eng.search("kubernetes operator pattern", top_k=3)
    assert any(r["id"] == "lx1" for r in res)


def test_hybrid_still_returns_vector_match():
    eng = _hybrid_engine()
    eng.store.upsert(
        [
            {
                "id": "x",
                "vector": eng.embedding.embed(["machine learning models"])[0],
                "payload": {"doc_url": "u", "doc_title": "t", "index": 0, "text": "ml"},
            }
        ]
    )
    res = eng.search("machine learning models", top_k=3)
    assert res and res[0]["id"] == "x"


def test_hybrid_off_by_default():
    eng = SearchEngine(
        store=InMemoryStore(),
        embedding=FakeEmbedding(dim=32),
        llm=FakeLLM(),
    )
    assert eng.lexical is None
    res = eng.search("anything", top_k=1)
    assert res == []  # empty store, no lexical index -> nothing
