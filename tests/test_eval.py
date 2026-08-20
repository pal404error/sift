"""Evaluate retrieval metrics + the end-to-end eval harness (offline fake providers)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from llm_search.eval import mrr, precision_at_k, recall_at_k

ROOT = Path(__file__).resolve().parent.parent


def test_recall_at_k_basic():
    assert recall_at_k(["a", "b"], ["a", "x", "b"], 3) == 1.0
    assert recall_at_k(["a", "b"], ["a"], 3) == 0.5
    assert recall_at_k([], ["a"], 3) == 0.0


def test_precision_at_k_basic():
    assert precision_at_k(["a"], ["a", "x"], 2) == 0.5
    assert precision_at_k(["a"], ["a"], 1) == 1.0
    assert precision_at_k(["a"], [], 2) == 0.0


def test_mrr_basic():
    assert mrr([["a"]], [["a"]]) == 1.0
    assert mrr([["a"]], [["x", "a"]]) == 0.5
    assert mrr([["a"], ["b"]], [["a"], ["b"]]) == 1.0
    assert mrr([["a"], ["b"]], [["b"], ["a"]]) == 0.0
    assert mrr([["a"]], [["x"]]) == 0.0


def test_mrr_requires_aligned_lists():
    import pytest

    with pytest.raises(ValueError):
        mrr([["a"]], [["a"], ["b"]])


def test_run_eval_script_runs_offline():
    result = subprocess.run(
        [sys.executable, "scripts/run_eval.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    report = __import__("json").loads(result.stdout)
    assert 0.0 <= report["mrr"] <= 1.0
    assert 0.0 <= report["recall@k"] <= 1.0
    assert report["n_queries"] == 4


def test_run_eval_with_gold_file():
    gold = ROOT / "tests" / "gold" / "eval_gold.json"
    result = subprocess.run(
        [sys.executable, "scripts/run_eval.py", "--gold", str(gold)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    report = __import__("json").loads(result.stdout)
    assert report["n_queries"] == 4
    assert report["mrr"] == 1.0


def test_run_eval_gate_passes_above_threshold():
    result = subprocess.run(
        [sys.executable, "scripts/run_eval.py", "--gate-mrr", "0.9"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_run_eval_gate_fails_when_mrr_low():
    # Relevant doc id is never indexed, so it can never be retrieved -> MRR 0.
    gold = {
        "docs": [
            {"id": "x", "text": "zebra quadrant xylophone walnut vault"},
            {"id": "y", "text": "octopus nebula fountain kettle ladder"},
        ],
        "queries": [
            {"query": "retrieval augmented generation vector index", "relevant": ["missing1"]},
            {"query": "web crawler robots rate limit polite", "relevant": ["missing2"]},
        ],
    }
    path = ROOT / "tests" / "_tmp_gold.json"
    path.write_text(__import__("json").dumps(gold))
    try:
        result = subprocess.run(
            [sys.executable, "scripts/run_eval.py", "--gold", str(path), "--gate-mrr", "0.5"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1, result.stdout + result.stderr
    finally:
        path.unlink()
