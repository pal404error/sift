from __future__ import annotations

import hashlib

from llm_search.config import Settings, get_settings
from llm_search.ingest import chunk_document, fetch_url
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
    ) -> None:
        self.store = store
        self.embedding = embedding
        self.llm = llm
        self.settings = settings or get_settings()
        self.reranker = reranker or build_reranker(self.settings)

    def _index_doc(self, doc) -> int:
        chunks = chunk_document(doc, self.settings.chunk_size, self.settings.chunk_overlap)
        if not chunks:
            return 0
        texts = [c.text for c in chunks]
        vectors = self.embedding.embed(texts)
        items = []
        for chunk, vec in zip(chunks, vectors, strict=True):
            cid = hashlib.sha256(f"{chunk.doc_url}:{chunk.index}".encode()).hexdigest()[:16]
            items.append(
                {
                    "id": cid,
                    "vector": vec,
                    "payload": {
                        "doc_url": chunk.doc_url,
                        "doc_title": chunk.doc_title,
                        "index": chunk.index,
                        "text": chunk.text,
                    },
                }
            )
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
        candidates = self.store.search(qvec, top_k=max(wide, top_k))
        return self.reranker.rerank(query, candidates, top_n=top_k)

    def ask(self, query: str, top_k: int = 5) -> dict:
        results = self.search(query, top_k=top_k)
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
