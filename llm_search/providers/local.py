from __future__ import annotations

from typing import Any

from llm_search.config import Settings, get_settings
from llm_search.providers.base import EmbeddingProvider


class LocalEmbedding(EmbeddingProvider):
    """Local, API-key-free embeddings via sentence-transformers.

    Lazily loads a ``SentenceTransformer`` (guarded optional dependency) so the
    rest of the package imports cleanly without torch installed. Vectors are
    L2-normalized for cosine similarity.
    """

    def __init__(
        self,
        model: str = "",
        dim: int | None = None,
        settings: Settings | None = None,
    ) -> None:
        s = settings or get_settings()
        self.model_name = model or s.embedding_model
        self.dim = dim or s.embedding_dim
        self._model: Any = None

    def _ensure(self) -> None:
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as e:  # pragma: no cover
                raise RuntimeError(
                    "sentence-transformers is required for the 'local' embedding provider"
                ) from e
            self._model = SentenceTransformer(self.model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        self._ensure()
        vectors = self._model.encode(  # type: ignore[union-attr]
            texts, normalize_embeddings=True, convert_to_numpy=True
        )
        return [v.tolist() for v in vectors]
