"""Qdrant vector database for document knowledge base."""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.config import settings

_client: QdrantClient | None = None


def get_qdrant() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=settings.QDRANT_URL, prefer_grpc=settings.QDRANT_GRPC)
    return _client


def ensure_collection(client: QdrantClient | None = None):
    """Create the collection if it does not exist."""
    c = client or get_qdrant()
    collections = c.get_collections().collections
    names = [col.name for col in collections]
    if settings.QDRANT_COLLECTION not in names:
        c.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=settings.EMBEDDING_DIMENSIONS,
                distance=Distance.COSINE,
            ),
        )


async def add_chunks_to_vector_db(chunks: list[dict]) -> None:
    """Upsert chunk vectors into Qdrant. Each chunk must have id (UUID), chunk_id, text, doc_name, vector."""
    client = get_qdrant()
    ensure_collection(client)
    points = [
        PointStruct(
            id=chunk["id"],
            vector=chunk["vector"],
            payload={
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "doc_name": chunk["doc_name"],
            },
        )
        for chunk in chunks
    ]
    client.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)


async def search_vector_db(query_vector: list[float], top_k: int | None = None, client: QdrantClient | None = None) -> list[dict]:
    """Search the knowledge base by vector; returns list of {score, chunk_id, text, doc_name}."""
    top_k = top_k or settings.VECTOR_SEARCH_TOP_K
    client = client or get_qdrant()
    response = client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        limit=top_k,
    )
    return [
        {
            "score": hit.score,
            "chunk_id": hit.payload.get("chunk_id", str(hit.id)) if hit.payload else str(hit.id),
            "text": hit.payload.get("text", "") if hit.payload else "",
            "doc_name": hit.payload.get("doc_name", "") if hit.payload else "",
        }
        for hit in response.points
    ]
