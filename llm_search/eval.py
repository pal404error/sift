from __future__ import annotations

import math


def recall_at_k(relevant: list[str], retrieved: list[str], k: int) -> float:
    """Fraction of relevant docs present in the top-k retrieved."""
    if not relevant:
        return 0.0
    top = set(retrieved[:k])
    hits = len(top & set(relevant))
    return hits / len(set(relevant))


def precision_at_k(relevant: list[str], retrieved: list[str], k: int) -> float:
    """Fraction of top-k retrieved docs that are relevant."""
    if k <= 0:
        return 0.0
    top = retrieved[:k]
    if not top:
        return 0.0
    hits = len(set(top) & set(relevant))
    return hits / len(top)


def mrr(queries: list[list[str]], retrieved_lists: list[list[str]]) -> float:
    """Mean Reciprocal Rank across queries.

    `queries[i]` is the list of relevant ids for query i; `retrieved_lists[i]` the ranked
    retrieval. Returns average of 1/rank of the first relevant hit (0 if none).
    """
    if len(queries) != len(retrieved_lists):
        raise ValueError("queries and retrieved_lists must align")
    if not queries:
        return 0.0
    total = 0.0
    for relevant, retrieved in zip(queries, retrieved_lists, strict=False):
        rel_set = set(relevant)
        rank = 0
        for i, doc_id in enumerate(retrieved, start=1):
            if doc_id in rel_set:
                rank = i
                break
        total += 1.0 / rank if rank else 0.0
    return total / len(queries)


def ndcg_at_k(relevant: list[str], retrieved: list[str], k: int) -> float:
    """Normalized Discounted Cumulative Gain at k (binary relevance).

    Rewards placing relevant docs higher in the ranking; normalized against the
    ideal ordering so the score is in [0, 1].
    """

    def dcg(rels: list[float]) -> float:
        return sum(r / math.log2(i + 2) for i, r in enumerate(rels))

    rel_set = set(relevant)
    gains = [1.0 if d in rel_set else 0.0 for d in retrieved[:k]]
    ideal = [1.0] * min(len(rel_set), k)
    denom = dcg(ideal)
    return dcg(gains) / denom if denom else 0.0


def evaluate_retrieval(
    relevant: list[str],
    retrieved: list[str],
    k: int = 5,
) -> dict[str, float]:
    """Convenience bundle of metrics for one query."""
    return {
        "recall@k": recall_at_k(relevant, retrieved, k),
        "precision@k": precision_at_k(relevant, retrieved, k),
        "ndcg@k": ndcg_at_k(relevant, retrieved, k),
    }
