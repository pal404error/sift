from __future__ import annotations

import math
import re

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class LexicalIndex:
    """Inverted-index lexical retriever (BM25-lite) with payload storage.

    Kept dependency-free so it works air-gapped and offline. The engine feeds it
    every chunk alongside the vector store; ``search`` returns ranked chunk ids
    that the engine fuses with the vector results via Reciprocal Rank Fusion.
    """

    def __init__(self) -> None:
        self._doc_tokens: dict[str, list[str]] = {}
        self._inverted: dict[str, list[str]] = {}
        self._payloads: dict[str, dict] = {}
        self._doc_count = 0

    def add(self, doc_id: str, text: str, payload: dict | None = None) -> None:
        tokens = _tokens(text)
        self._doc_tokens[doc_id] = tokens
        for tok in set(tokens):
            self._inverted.setdefault(tok, []).append(doc_id)
        if payload is not None:
            self._payloads[doc_id] = payload
        self._doc_count += 1

    def search(self, query: str, top_n: int = 10) -> list[tuple[str, float]]:
        q_tokens = _tokens(query)
        if not q_tokens:
            return []
        n = self._doc_count or 1
        scores: dict[str, float] = {}
        for qt in set(q_tokens):
            postings = self._inverted.get(qt, [])
            if not postings:
                continue
            idf = math.log((n - len(postings) + 0.5) / (len(postings) + 0.5) + 1.0)
            for doc_id in postings:
                tf = self._doc_tokens[doc_id].count(qt)
                scores[doc_id] = scores.get(doc_id, 0.0) + idf * (tf * 2.0) / (tf + 1.0)
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        return ranked[:top_n]

    def payload(self, doc_id: str) -> dict | None:
        return self._payloads.get(doc_id)

    def count(self) -> int:
        return self._doc_count
