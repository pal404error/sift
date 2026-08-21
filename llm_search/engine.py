from __future__ import annotations

import hashlib
from collections.abc import Iterator

from llm_search.config import Settings, get_settings
from llm_search.ingest import chunk_document, fetch_url
from llm_search.lexical_index import LexicalIndex
from llm_search.providers.base import EmbeddingProvider, LLMProvider
from llm_search.rerank import Reranker, build_reranker
from llm_search.store.base import VectorStore


class SearchEngine:
    def __init__(
        self,
        store: VectorStore,
        embedding: EmbeddingProvider,
        llm: LLMProvider,
        settings: Settings | None = None,
        reranker: Reranker | None = None,
        lexical: LexicalIndex | None = None,
        hybrid: bool | None = None,
    ) -> None:
        self.store = store
        self.embedding = embedding
        self.llm = llm
        self.settings = settings or get_settings()
        self.reranker = reranker or build_reranker(self.settings)
        self.lexical = lexical
        if self.lexical is None and (hybrid if hybrid is not None else self.settings.hybrid):
            self.lexical = LexicalIndex()

    def _index_doc(self, doc) -> int:
        chunks = chunk_document(doc, self.settings.chunk_size, self.settings.chunk_overlap)
        if not chunks:
            return 0
        texts = [c.text for c in chunks]
        vectors = self.embedding.embed(texts)
        items = []
        for chunk, vec in zip(chunks, vectors, strict=True):
            cid = hashlib.sha256(f"{chunk.doc_url}:{chunk.index}".encode()).hexdigest()[:16]
            payload = {
                "doc_url": chunk.doc_url,
                "doc_title": chunk.doc_title,
                "index": chunk.index,
                "text": chunk.text,
            }
            items.append({"id": cid, "vector": vec, "payload": payload})
            if self.lexical is not None:
                self.lexical.add(cid, chunk.text, payload)
        self.store.upsert(items)
        return len(items)

    def ingest_url(self, url: str) -> int:
        doc = fetch_url(
            url,
            respect_robots=self.settings.respect_robots,
            min_interval=self.settings.min_crawl_interval,
        )
        return self._index_doc(doc)

    def crawl_site(self, start_url: str, max_pages: int | None = None) -> dict:
        from llm_search.crawl import crawl_site as _crawl

        max_pages = max_pages or self.settings.max_pages_per_ingest
        _, stats = _crawl(
            start_url,
            ingest_fn=self._index_doc,
            max_pages=max_pages,
            concurrency=self.settings.crawl_concurrency,
        )
        return stats

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        qvec = self.embedding.embed([query])[0]
        wide = top_k * self.settings.rerank_multiplier
        vector_hits = self.store.search(qvec, top_k=max(wide, top_k))
        if self.lexical is None:
            return self.reranker.rerank(query, vector_hits, top_n=top_k)

        # Hybrid: fuse vector + lexical ranks via Reciprocal Rank Fusion (RRF).
        lexical_hits = self.lexical.search(query, top_n=max(wide, top_k))
        fused: dict[str, float] = {}
        for rank, hit in enumerate(vector_hits):
            fused[hit["id"]] = fused.get(hit["id"], 0.0) + 1.0 / (self.settings.rrf_k + rank + 1)
        for rank, (doc_id, _score) in enumerate(lexical_hits):
            fused[doc_id] = fused.get(doc_id, 0.0) + 1.0 / (self.settings.rrf_k + rank + 1)

        ordered = sorted(fused.keys(), key=lambda i: fused[i], reverse=True)
        by_id = {h["id"]: h for h in vector_hits}
        candidates = []
        for cid in ordered:
            if cid in by_id:
                candidates.append(by_id[cid])
            elif (p := self.lexical.payload(cid)) is not None:
                candidates.append({"id": cid, "score": fused[cid], "payload": p})
        return self.reranker.rerank(query, candidates, top_n=top_k)

    def ask(self, query: str, top_k: int = 5, use_hyde: bool | None = None) -> dict:
        use_hyde = self.settings.use_hyde if use_hyde is None else use_hyde
        search_query = query
        if use_hyde:
            # Hypothetical Document Embeddings: rewrite the query into a short, plausible
            # answer passage, then embed THAT. Denser semantic match than the raw question.
            hypo = self.llm.generate(
                system=(
                    "You are a precise assistant. Write a single short, factual passage "
                    "that could answer the question. No preamble."
                ),
                prompt=f"Question: {query}\nPassage:",
            )
            search_query = f"{query}\n{hypo}"
        results = self.search(search_query, top_k=top_k)
        context = "\n\n".join(
            f"[{r['payload'].get('doc_title', '')}] {r['payload'].get('text', '')}" for r in results
        )
        if not results:
            return {"answer": "No relevant context found.", "sources": []}
        system = (
            "You are a precise search assistant. Answer ONLY using the provided context. "
            "If the context is insufficient, say you don't know. Cite source URLs."
        )
        prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
        answer = self.llm.generate(system=system, prompt=prompt)
        return {"answer": answer, "sources": [r["payload"].get("doc_url") for r in results]}

    def ask_stream(
        self, query: str, top_k: int = 5, use_hyde: bool | None = None
    ) -> Iterator[dict]:
        """Stream an answer as SSE-friendly events.

        Yields ``{"type": "sources", "sources": [...]}`` first (once retrieval is done),
        then ``{"type": "token", "text": "..."}`` chunks as the LLM generates. Retrieval
        is identical to :meth:`ask`; only answer generation is incremental.
        """
        use_hyde = self.settings.use_hyde if use_hyde is None else use_hyde
        search_query = query
        if use_hyde:
            hypo = self.llm.generate(
                system=(
                    "You are a precise assistant. Write a single short, factual passage "
                    "that could answer the question. No preamble."
                ),
                prompt=f"Question: {query}\nPassage:",
            )
            search_query = f"{query}\n{hypo}"
        results = self.search(search_query, top_k=top_k)
        yield {"type": "sources", "sources": [r["payload"].get("doc_url") for r in results]}
        if not results:
            yield {"type": "token", "text": "No relevant context found."}
            return
        context = "\n\n".join(
            f"[{r['payload'].get('doc_title', '')}] {r['payload'].get('text', '')}" for r in results
        )
        system = (
            "You are a precise search assistant. Answer ONLY using the provided context. "
            "If the context is insufficient, say you don't know. Cite source URLs."
        )
        prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
        for chunk in self.llm.stream(system=system, prompt=prompt):
            yield {"type": "token", "text": chunk}
