import pytest

faiss = pytest.importorskip("faiss")

# faiss-cpu and torch (sentence-transformers) segfault when loaded in the same process
# due to a BLAS/OpenBLAS conflict. Skip these tests if torch is importable so the suite
# stays green in environments that have both optional extras installed. In a faiss-only
# environment (no torch) these tests run normally.
try:
    import torch  # noqa: F401

    pytest.skip(
        "faiss tests skipped: torch importable (faiss/torch same-process segfault conflict)",
        allow_module_level=True,
    )
except ImportError:
    pass

from llm_search.config import Settings  # noqa: E402
from llm_search.engine import SearchEngine  # noqa: E402
from llm_search.providers.base import cosine_similarity  # noqa: E402
from llm_search.providers.fake import FakeEmbedding, FakeLLM  # noqa: E402
from llm_search.store import build_store  # noqa: E402
from llm_search.store.faiss_store import FaissStore  # noqa: E402


def _make_settings():
    return Settings(
        llm_provider="fake",
        embedding_provider="fake",
        require_auth=False,
        respect_robots=False,
    )


def test_build_store_selects_faiss():
    s = _make_settings()
    s.vector_store = "faiss"
    store = build_store(s)
    assert isinstance(store, FaissStore)


def test_faiss_store_matches_cosine_ranking():
    # IndexFlatIP with normalized vectors == cosine similarity -> same ranking as
    # the pure-Python InMemoryStore.
    store = FaissStore(dim=4)
    items = [
        {"id": "a", "vector": [1.0, 0.0, 0.0, 0.0], "payload": {"doc_url": "a"}},
        {"id": "b", "vector": [0.9, 0.1, 0.0, 0.0], "payload": {"doc_url": "b"}},
        {"id": "c", "vector": [0.0, 1.0, 0.0, 0.0], "payload": {"doc_url": "c"}},
    ]
    store.upsert(items)
    assert store.count() == 3
    q = [1.0, 0.05, 0.0, 0.0]
    res = store.search(q, top_k=3)
    assert res[0]["id"] == "a"  # closest to query
    # scores equal cosine computed directly
    assert abs(res[0]["score"] - cosine_similarity(q, items[0]["vector"])) < 1e-5


def test_faiss_store_upsert_replaces_existing_id():
    store = FaissStore(dim=2)
    store.upsert([{"id": "x", "vector": [1.0, 0.0], "payload": {"v": 1}}])
    store.upsert([{"id": "x", "vector": [0.0, 1.0], "payload": {"v": 2}}])
    assert store.count() == 1  # replaced, not duplicated
    res = store.search([0.0, 1.0], top_k=1)
    assert res[0]["payload"] == {"v": 2}


def test_faiss_store_empty_search_returns_empty():
    store = FaissStore(dim=2)
    assert store.search([1.0, 0.0], top_k=5) == []


def test_engine_works_end_to_end_with_faiss():
    s = _make_settings()
    s.vector_store = "faiss"
    eng = SearchEngine(build_store(s), FakeEmbedding(), FakeLLM(), settings=s)
    from llm_search.ingest.fetch import Document

    eng._index_doc(
        Document(url="http://a", title="A", text="the quick brown fox jumps over the lazy dog")
    )
    eng._index_doc(
        Document(
            url="http://b",
            title="B",
            text="photosynthesis converts sunlight into chemical energy",
        )
    )
    results = eng.search("quick brown fox", top_k=1)
    assert results and results[0]["payload"]["doc_url"] == "http://a"
