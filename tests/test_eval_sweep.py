import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_embedding_sweep_skips_unloadable_model():
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_eval.py",
            "--embedding-models",
            "not-a-real-model-xyz",
            "--gold",
            "tests/gold/eval_gold_semantic.json",
            "--k",
            "5",
        ],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0
    assert "skipped" in result.stderr.lower()
