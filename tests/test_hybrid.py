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


def test_weighted_fusion_mode_surfaces_lexical_only_match():
    eng = _hybrid_engine()
    eng.settings.hybrid_mode = "weighted"
    eng.settings.hybrid_alpha = 0.0  # pure lexical
    eng.lexical.add(  # only in the lexical index
        "lx1",
        "kubernetes operator pattern",
        {"doc_url": "u", "doc_title": "t", "index": 0, "text": "kubernetes operator pattern"},
    )
    res = eng.search("kubernetes operator pattern", top_k=3)
    assert any(r["id"] == "lx1" for r in res)


def test_weighted_fuse_blend_respects_alpha():
    vec = [{"id": "a", "score": 0.9}, {"id": "b", "score": 0.1}]
    lex = [("a", 0.2), ("b", 0.8)]
    pure_lex = SearchEngine._weighted_fuse(vec, lex, alpha=0.0)
    assert pure_lex["b"] > pure_lex["a"]  # lexical leader wins when alpha=0
    pure_vec = SearchEngine._weighted_fuse(vec, lex, alpha=1.0)
    assert pure_vec["a"] > pure_vec["b"]  # vector leader wins when alpha=1


def test_looks_lexical_detects_codes():
    assert SearchEngine._looks_lexical("Outlook 2019 sync error 0x80004005")
    assert SearchEngine._looks_lexical("rollback runbook for v3.2 deployment")
    assert not SearchEngine._looks_lexical("what is retrieval augmented generation")


def test_query_routing_surfaces_lexical_only_on_code_query():
    eng = _hybrid_engine()
    eng.settings.hybrid_mode = "weighted"
    eng.settings.hybrid_alpha = 1.0  # pure vector by default
    eng.settings.hybrid_route = True
    eng.lexical.add(
        "code1",
        "error 0x80004005 troubleshooting",
        {"doc_url": "u", "doc_title": "t", "index": 0, "text": "error 0x80004005"},
    )
    # Without routing, alpha=1.0 (pure vector) would miss the lexical-only doc.
    # With routing on a code query, alpha is capped at 0.3 -> lexical wins.
    res = eng.search("Outlook 2019 sync error 0x80004005", top_k=3)
    assert any(r["id"] == "code1" for r in res)


def test_hybrid_off_by_default():
    eng = SearchEngine(
        store=InMemoryStore(),
        embedding=FakeEmbedding(dim=32),
        llm=FakeLLM(),
    )
    assert eng.lexical is None
    res = eng.search("anything", top_k=1)
    assert res == []  # empty store, no lexical index -> nothing
