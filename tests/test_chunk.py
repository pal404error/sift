from __future__ import annotations

from llm_search.ingest import Document, chunk_document


def test_chunk_respects_size_and_overlap():
    doc = Document(url="u", title="t", text=" ".join(f"w{i}" for i in range(100)))
    chunks = chunk_document(doc, chunk_size=10, overlap=2)
    assert chunks[0].text.count(" ") + 1 == 10
    # overlap: chunk1 must start with the last `overlap` words of chunk0
    last_of_prev = chunks[0].text.split()[-2:]
    first_of_next = chunks[1].text.split()[:2]
    assert first_of_next == last_of_prev


def test_empty_document_yields_no_chunks():
    doc = Document(url="u", title="t", text="")
    assert chunk_document(doc) == []


def test_chunk_index_monotonic():
    doc = Document(url="u", title="t", text=" ".join(f"w{i}" for i in range(50)))
    chunks = chunk_document(doc, chunk_size=10, overlap=2)
    assert [c.index for c in chunks] == list(range(len(chunks)))
