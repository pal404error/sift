.PHONY: install lint type test cov audit eval ci docker pre-commit

install:
	pip install -e ".[dev]"

lint:
	ruff check .

type:
	mypy .

test:
	pytest -q

cov:
	pytest --cov=llm_search --cov-fail-under=80

audit:
	pip-audit

eval:
	python scripts/run_eval.py --gate-mrr 0.5

ci: lint type cov audit eval

docker:
	docker build -t llm-search:local .

pre-commit:
	pre-commit run --all-files
