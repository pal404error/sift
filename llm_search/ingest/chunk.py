from __future__ import annotations

from dataclasses import dataclass

from llm_search.ingest.fetch import Document


@dataclass
class Chunk:
    doc_url: str
    doc_title: str
    text: str
    index: int


def chunk_document(doc: Document, chunk_size: int = 400, overlap: int = 64) -> list[Chunk]:
    """Word-based chunking with overlap. chunk_size/overlap are word counts."""
    words = doc.text.split()
    if not words:
        return []
    step = max(1, chunk_size - overlap)
    chunks: list[Chunk] = []
    idx = 0
    i = 0
    while i < len(words):
        piece = words[i : i + chunk_size]
        chunks.append(Chunk(doc_url=doc.url, doc_title=doc.title, text=" ".join(piece), index=idx))
        idx += 1
        i += step
    return chunks
