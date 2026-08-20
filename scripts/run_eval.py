"""Run the retrieval eval harness end-to-end (fully offline with fake providers).

Builds an in-memory index from a gold corpus, runs each gold query through the
real `SearchEngine.search` -> reranker -> `evaluate_retrieval` path, and reports
recall@k / precision@k / MRR.

With the default fake (lexical) embeddings this validates the whole pipeline and
gives token-overlap-based numbers. Point `--gold` at a real annotated corpus and
set real providers (LLM_PROVIDER/EMBEDDING_PROVIDER) for true relevance scores.

Usage:
    python scripts/run_eval.py                 # embedded demo gold set
    python scripts/run_eval.py --gold gold.jsonl --k 10 --gate-mrr 0.8
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace

from llm_search.config import get_settings
from llm_search.engine import SearchEngine
from llm_search.eval import mrr, precision_at_k, recall_at_k
from llm_search.providers.fake import FakeEmbedding, FakeLLM
from llm_search.rerank import build_reranker
from llm_search.store.memory import InMemoryStore

EMBEDDED_GOLD: dict = {
    "docs": [
        {
            "id": "rag",
            "text": (
                "Retrieval augmented generation combines a vector search index with a "
                "large language model to answer questions over private documents."
            ),
        },
        {
            "id": "rerank",
            "text": (
                "A reranker reorders the top candidate passages using a cross encoder "
                "model to improve answer relevance for the search query."
            ),
        },
        {
            "id": "crawl",
            "text": (
                "A web crawler fetches pages respecting robots dot txt and a per host "
                "rate limit to ingest web sites politely without overloading servers."
            ),
        },
        {
            "id": "oidc",
            "text": (
                "OIDC single sign on verifies a JWT token signature against a JWKS "
                "public key for enterprise authentication and authorization."
            ),
        },
    ],
    "queries": [
        {"query": "what is retrieval augmented generation", "relevant": ["rag"]},
        {"query": "how does a reranker improve answer relevance", "relevant": ["rerank"]},
        {"query": "how does a web crawler stay polite", "relevant": ["crawl"]},
        {"query": "how does OIDC authentication verify tokens", "relevant": ["oidc"]},
    ],
}


def load_gold(path: str | None) -> dict:
    if not path:
        return EMBEDDED_GOLD
    data = json.loads(Path(path).read_text())
    if "docs" in data and "queries" in data:
        return data
    # jsonl: each line {"id","text"} or {"query","relevant":[...]}
    docs: list[dict] = []
    queries: list[dict] = []
    for line in data if isinstance(data, list) else [data]:
        if "query" in line:
            queries.append(line)
        else:
            docs.append(line)
    return {"docs": docs, "queries": queries}


def run_eval(gold: dict, k: int = 5) -> dict:
    settings = get_settings()
    engine = SearchEngine(
        InMemoryStore(),
        FakeEmbedding(),
        FakeLLM(),
        settings,
        build_reranker(settings),
    )
    for d in gold["docs"]:
        doc = SimpleNamespace(url=d["id"], title=d.get("title", d["id"]), text=d["text"])
        engine._index_doc(doc)

    relevant_lists: list[list[str]] = []
    retrieved_lists: list[list[str]] = []
    for q in gold["queries"]:
        results = engine.search(q["query"], top_k=k)
        retrieved = [r["payload"]["doc_url"] for r in results]
        retrieved_lists.append(retrieved)
        relevant_lists.append(q["relevant"])

    recall = sum(
        recall_at_k(r, ret, k) for r, ret in zip(relevant_lists, retrieved_lists, strict=True)
    )
    prec = sum(
        precision_at_k(r, ret, k) for r, ret in zip(relevant_lists, retrieved_lists, strict=True)
    )
    n = len(relevant_lists) or 1
    return {
        "k": k,
        "n_queries": len(relevant_lists),
        "recall@k": recall / n,
        "precision@k": prec / n,
        "mrr": mrr(relevant_lists, retrieved_lists),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Run the offline retrieval eval harness.")
    ap.add_argument("--gold", help="Path to gold JSON/JSONL (docs+queries).")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument(
        "--gate-mrr",
        type=float,
        default=None,
        help="Exit non-zero if MRR is below this threshold.",
    )
    args = ap.parse_args()

    gold = load_gold(args.gold)
    report = run_eval(gold, k=args.k)
    print(json.dumps(report, indent=2))

    if args.gate_mrr is not None and report["mrr"] < args.gate_mrr:
        print(f"GATE FAILED: mrr {report['mrr']:.3f} < {args.gate_mrr}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
