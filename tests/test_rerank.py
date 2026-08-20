from __future__ import annotations

from llm_search.rerank import (
    CrossEncoderReranker,
    FakeReranker,
    LexicalReranker,
    build_reranker,
)


def _item(text: str, id_: str) -> dict:
    return {"id": id_, "score": 0.5, "payload": {"text": text}}


def test_lexical_reranker_prefers_overlap():
    items = [
        _item("the cat sat on the mat", "a"),
        _item("quantum computing uses qubits", "b"),
        _item("cat mat furry animal", "c"),
    ]
    r = LexicalReranker().rerank("cat mat", items, top_n=2)
    ids = [i["id"] for i in r]
    assert "a" in ids and "c" in ids
    assert "b" not in ids


def test_lexical_reranker_empty_query_passthrough():
    items = [_item("x", "a"), _item("y", "b")]
    assert LexicalReranker().rerank("", items, top_n=1) == items[:1]


def test_fake_reranker_passthrough():
    items = [_item("x", "a"), _item("y", "b")]
    assert FakeReranker().rerank("q", items, top_n=5) == items[:5]


def test_build_reranker_dispatch():
    from llm_search.config import Settings

    assert isinstance(build_reranker(Settings(reranker="lexical")), LexicalReranker)
    assert isinstance(build_reranker(Settings(reranker="none")), FakeReranker)
    assert isinstance(build_reranker(Settings(reranker="fake")), FakeReranker)
    assert isinstance(build_reranker(Settings(reranker="cross-encoder")), CrossEncoderReranker)


def test_cross_encoder_reranker_uses_injected_scorer():
    items = [
        _item("the cat sat on the mat", "a"),
        _item("quantum computing uses qubits", "b"),
        _item("cat mat furry animal", "c"),
    ]

    def scorer(pairs):
        # reward chunks containing both query words
        out = []
        for q, text in pairs:
            words = set(q.lower().split())
            out.append(float(len(words & set(text.lower().split()))))
        return out

    r = CrossEncoderReranker(scorer=scorer)
    ranked = r.rerank("cat mat", items, top_n=2)
    ids = [i["id"] for i in ranked]
    assert ids == ["a", "c"]


def test_cross_encoder_reranker_empty():
    assert CrossEncoderReranker(scorer=lambda p: []).rerank("q", [], top_n=5) == []
