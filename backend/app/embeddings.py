"""Embeddings using BAAI/bge-small-en-v1.5 via sentence-transformers."""
import asyncio
from sentence_transformers import SentenceTransformer
from app.config import settings

_model: SentenceTransformer | None = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model


def _encode(text: str) -> list[float]:
    return _get_model().encode(text, convert_to_numpy=True).tolist()


def _encode_batch(texts: list[str]) -> list[list[float]]:
    return _get_model().encode(texts, convert_to_numpy=True).tolist()


async def get_embedding(input: str, **kwargs) -> list[float]:
    """Return embedding vector for a single string (async)."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _encode, input)


async def get_embeddings(input: list[str], **kwargs) -> list[list[float]]:
    """Return embedding vectors for a list of strings (async)."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _encode_batch, input)
