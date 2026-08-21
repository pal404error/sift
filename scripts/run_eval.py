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

from llm_search.config import Settings, get_settings
from llm_search.engine import SearchEngine
from llm_search.eval import mrr, ndcg_at_k, precision_at_k, recall_at_k
from llm_search.providers.fake import FakeEmbedding, FakeLLM
from llm_search.providers.local import LocalEmbedding
from llm_search.rerank import CrossEncoderReranker, build_reranker
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


def run_eval(
    gold: dict,
    k: int = 5,
    rerank_multiplier: int | None = None,
    embedding=None,
    reranker=None,
) -> dict:
    settings = get_settings()
    if rerank_multiplier is not None:
        settings = Settings(rerank_multiplier=rerank_multiplier)
    engine = SearchEngine(
        InMemoryStore(),
        embedding or FakeEmbedding(),
        FakeLLM(),
        settings,
        reranker or build_reranker(settings),
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
    ndcg = sum(
        ndcg_at_k(r, ret, k) for r, ret in zip(relevant_lists, retrieved_lists, strict=True)
    )
    n = len(relevant_lists) or 1
    return {
        "k": k,
        "n_queries": len(relevant_lists),
        "recall@k": recall / n,
        "precision@k": prec / n,
        "ndcg@k": ndcg / n,
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
    ap.add_argument(
        "--rerank-multipliers",
        type=str,
        default=None,
        help="Comma-separated multipliers to sweep (e.g. '1,3,5,10'); prints a comparison table.",
    )
    ap.add_argument(
        "--embedding",
        choices=["fake", "local"],
        default="fake",
        help="Embedding provider for the run (local = sentence-transformers MiniLM).",
    )
    ap.add_argument(
        "--embedding-models",
        type=str,
        default=None,
        help=(
            "Comma-separated sentence-transformers model names to sweep (semantic, "
            "cross-encoder reranker). Builds a fresh index per model and prints a "
            "comparison. Skips models that fail to load (e.g. download error)."
        ),
    )
    ap.add_argument(
        "--reranker",
        choices=["lexical", "cross-encoder"],
        default="lexical",
        help="Reranker for the run.",
    )
    ap.add_argument(
        "--compare",
        action="store_true",
        help="Print a side-by-side table: fake+lexical vs local+cross-encoder.",
    )
    args = ap.parse_args()

    gold = load_gold(args.gold)

    if args.embedding_models:
        names = [x.strip() for x in args.embedding_models.split(",") if x.strip()]
        print(f"embedding model sweep (k={args.k}, cross-encoder reranker):")
        print(f"{'model':<48}{'recall@k':>10}{'precision@k':>12}{'ndcg@k':>9}{'mrr':>7}")
        for name in names:
            try:
                rep = run_eval(
                    gold,
                    k=args.k,
                    embedding=LocalEmbedding(model=name),
                    reranker=CrossEncoderReranker(),
                )
            except Exception as e:  # model download/load failure, OOM, etc.
                print(f"  ! skipped {name}: {type(e).__name__}: {e}", file=sys.stderr)
                continue
            print(
                f"{name:<48}{rep['recall@k']:>10.3f}{rep['precision@k']:>12.3f}"
                f"{rep['ndcg@k']:>9.3f}{rep['mrr']:>7.3f}"
            )
        return 0

    if args.compare:
        base = run_eval(
            gold,
            k=args.k,
            embedding=FakeEmbedding(),
            reranker=build_reranker(Settings(reranker="lexical")),
        )
        sem = run_eval(
            gold,
            k=args.k,
            embedding=LocalEmbedding(),
            reranker=CrossEncoderReranker(),
        )
        print(f"{'config':<26}{'recall@k':>10}{'precision@k':>12}{'ndcg@k':>9}{'mrr':>7}")

        def _row(label: str, r: dict) -> str:
            return (
                f"{label:<26}{r['recall@k']:>10.3f}{r['precision@k']:>12.3f}"
                f"{r['ndcg@k']:>9.3f}{r['mrr']:>7.3f}"
            )

        print(_row("fake + lexical", base))
        print(_row("local + cross-encoder", sem))
        return 0


    embedding = LocalEmbedding() if args.embedding == "local" else FakeEmbedding()
    reranker = build_reranker(Settings(reranker=args.reranker))

    if args.rerank_multipliers:
        mults = [int(float(x)) for x in args.rerank_multipliers.split(",") if x.strip()]
        rows = []
        for m in mults:
            rep = run_eval(
                gold,
                k=args.k,
                rerank_multiplier=m,
                embedding=embedding,
                reranker=reranker,
            )
            rows.append((m, rep["recall@k"], rep["precision@k"], rep["mrr"]))
        best = max(rows, key=lambda r: r[3])
        print(f"rerank_multiplier sweep (k={args.k}, {args.embedding}+{args.reranker}):")
        print(f"{'mult':>6} {'recall@k':>10} {'precision@k':>12} {'mrr':>6}")
        for m, rec, prec, mrr in rows:
            print(f"{m:>6.1f} {rec:>10.3f} {prec:>12.3f} {mrr:>6.3f}")
        print(f"best mrr at rerank_multiplier={best[0]:.1f}")
        return 0

    report = run_eval(gold, k=args.k, embedding=embedding, reranker=reranker)
    print(json.dumps(report, indent=2))

    if args.gate_mrr is not None and report["mrr"] < args.gate_mrr:
        print(f"GATE FAILED: mrr {report['mrr']:.3f} < {args.gate_mrr}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
