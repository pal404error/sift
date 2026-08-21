"""Convert a BEIR dataset into Sift's eval gold format.

BEIR ships ground-truth relevance judgments (qrels), so the relevance labels are NOT
authored by us — this is a genuinely external, verifiable benchmark. We sample queries,
keep their relevant docs, and add a bounded pool of distractor docs so retrieval is non-trivial.

Usage:
    python scripts/import_beir.py --dataset scifact --sample 100 --max-docs 2000
    python scripts/run_eval.py --gold tests/gold/eval_gold_beir_scifact.json --compare

The generated gold file is large and regenerable; it is git-ignored (see .gitignore).
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from beir import util
from beir.datasets.data_loader import GenericDataLoader


def build_gold(
    corpus: dict,
    queries: dict,
    qrels: dict,
    name: str = "beir",
    sample: int = 100,
    max_docs: int = 2000,
    seed: int = 42,
) -> dict:
    """Pure conversion: BEIR structures -> Sift gold dict. No network."""
    rng = random.Random(seed)
    qids = [q for q in queries if q in qrels and any(v > 0 for _k, v in qrels[q].items())]
    rng.shuffle(qids)
    chosen = qids[:sample]

    relevant_ids = {d for qid in chosen for d, r in qrels[qid].items() if r > 0}
    distractor_pool = [d for d in corpus if d not in relevant_ids]
    rng.shuffle(distractor_pool)
    selected = list(relevant_ids) + distractor_pool[: max(0, max_docs - len(relevant_ids))]
    selected = selected[:max_docs]

    docs = []
    for doc_id in selected:
        c = corpus[doc_id]
        text = (c.get("title", "") + ". " + c.get("text", "")).strip().lstrip(". ").strip()
        if text:
            docs.append({"id": doc_id, "text": text})

    gold_queries = []
    for qid in chosen:
        rels = [d for d, r in qrels[qid].items() if r and d in selected]
        if rels:
            gold_queries.append({"id": qid, "query": queries[qid], "relevant": rels})

    return {
        "meta": {
            "name": f"beir_{name}",
            "source": f"BEIR {name} (ground-truth qrels), external",
            "note": "Relevance is BEIR ground truth, not authored. Corpus capped at "
            f"{max_docs} docs (relevant + sampled distractors).",
            "n_docs": len(docs),
            "n_queries": len(gold_queries),
        },
        "docs": docs,
        "queries": gold_queries,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Convert a BEIR dataset to Sift gold format.")
    ap.add_argument("--dataset", default="scifact", help="BEIR dataset name (e.g. scifact).")
    ap.add_argument("--split", default="test")
    ap.add_argument("--sample", type=int, default=100, help="Number of queries to sample.")
    ap.add_argument(
        "--max-docs", type=int, default=2000, help="Max corpus size (relevant + distractors)."
    )
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument(
        "--out",
        default=None,
        help="Output path (default tests/gold/eval_gold_beir_<dataset>.json).",
    )
    args = ap.parse_args()

    url = f"https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{args.dataset}.zip"
    data_path = util.download_and_unzip(url, args.dataset)
    corpus, queries, qrels = GenericDataLoader(data_folder=data_path).load(split=args.split)

    gold = build_gold(
        corpus, queries, qrels,
        name=args.dataset, sample=args.sample, max_docs=args.max_docs, seed=args.seed,
    )
    out = Path(args.out or f"tests/gold/eval_gold_beir_{args.dataset}.json")
    out.write_text(json.dumps(gold, indent=2))
    print(f"wrote {out} ({gold['meta']['n_docs']} docs, {gold['meta']['n_queries']} queries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
