import logging

from meshmind.core.config import settings

logger = logging.getLogger(__name__)

FALLBACK_DIM = settings.embedding_dim  # 1024


class EmbeddingEncoder:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.embedding_model
        self._model = None
        self._available = True

    @property
    def model(self):
        if self._model is None and self._available:
            try:
                import os
                os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name, device="cpu")
                logger.info("BGE-M3 encoder loaded successfully")
            except Exception as e:
                self._available = False
                logger.warning(f"BGE-M3 unavailable ({e}), using fallback zero vectors")
        return self._model if self._available else None

    def encode(self, texts: str | list[str], batch_size: int = 32) -> list[list[float]]:
        if isinstance(texts, str):
            texts = [texts]
        m = self.model
        if m is not None:
            embeddings = m.encode(
                texts, batch_size=batch_size,
                normalize_embeddings=True, show_progress_bar=False,
            )
            return embeddings.tolist()
        return [[0.0] * FALLBACK_DIM for _ in texts]

    def encode_single(self, text: str) -> list[float]:
        return self.encode(text)[0]
