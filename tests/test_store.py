from __future__ import annotations

from llm_search.store import InMemoryStore


def test_memory_store_upsert_search_roundtrip():
    store = InMemoryStore()
    store.upsert(
        [
            {"id": "a", "vector": [1.0, 0.0], "payload": {"text": "alpha"}},
            {"id": "b", "vector": [0.0, 1.0], "payload": {"text": "beta"}},
        ]
    )
    res = store.search([0.9, 0.1], top_k=1)
    assert res[0]["id"] == "a"
    assert store.count() == 2


def test_memory_store_upsert_dedup_by_id():
    store = InMemoryStore()
    store.upsert([{"id": "a", "vector": [1.0, 0.0], "payload": {"text": "x"}}])
    store.upsert([{"id": "a", "vector": [1.0, 0.0], "payload": {"text": "y"}}])
    assert store.count() == 1
