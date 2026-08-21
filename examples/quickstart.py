"""Minimal end-to-end Sift demo — no API keys required.

Exercises the headline features with the built-in fake providers:
hybrid retrieval (lexical + vector), HyDE query expansion, and streaming
answers. Swap in real providers via environment variables (see README).
"""

from __future__ import annotations

from types import SimpleNamespace

from llm_search.engine import SearchEngine
from llm_search.providers import FakeEmbedding, FakeLLM
from llm_search.store import InMemoryStore


def main() -> None:
    engine = SearchEngine(
        store=InMemoryStore(),
        embedding=FakeEmbedding(dim=32),
        llm=FakeLLM(),
        hybrid=True,  # also settable via SIFT_HYBRID=true
    )

    docs = [
        SimpleNamespace(
            url="https://example.com/rag",
            title="RAG",
            text="Retrieval augmented generation combines a vector index with a language model.",
        ),
        SimpleNamespace(
            url="https://example.com/hyde",
            title="HyDE",
            text="Hypothetical Document Embeddings rewrite the query into an answer passage.",
        ),
    ]
    for d in docs:
        engine._index_doc(d)

    q = "how does retrieval augmented generation work?"
    print("== search (hybrid) ==")
    for r in engine.search(q, top_k=2):
        print(f" - {r['payload']['doc_title']}: {r['payload']['text']}")

    print("\n== ask (HyDE + streaming) ==")
    for ev in engine.ask_stream(q, use_hyde=True):
        if ev["type"] == "sources":
            print("sources:", ev["sources"])
        else:
            print(ev["text"], end="", flush=True)
    print()


if __name__ == "__main__":
    main()
