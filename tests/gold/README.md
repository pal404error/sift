# Eval gold sets

- `eval_gold_semantic.json` — small authored set (paraphrases/synonyms/multi-hop). Committed.
- `eval_gold_large.json` — larger authored factual + multilingual set. Committed.
- `eval_gold_beir_*.json` — **regenerable, git-ignored** (large). Generated from BEIR with
  ground-truth qrels (relevance not authored by us). Regenerate:

  ```bash
  pip install beir
  python scripts/import_beir.py --dataset scifact --sample 100 --max-docs 2000
  python scripts/run_eval.py --gold tests/gold/eval_gold_beir_scifact.json --compare
  ```

All gold files are validated by `tests/test_gold_integrity.py`.
