from __future__ import annotations

import pytest

from llm_search.engine import SearchEngine
from llm_search.providers import FakeEmbedding, FakeLLM
from llm_search.store import InMemoryStore


@pytest.fixture
def engine() -> SearchEngine:
    return SearchEngine(
        store=InMemoryStore(),
        embedding=FakeEmbedding(dim=32),
        llm=FakeLLM(),
    )
