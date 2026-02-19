"""PDF ingestion: extract text, chunk, embed, and upsert into Qdrant."""
from io import BytesIO
from uuid import uuid4
from pdfminer.high_level import extract_text
from app.utils.splitter import FixedSizeCharSplitter
from app.embeddings import get_embeddings
from app.vector_db import add_chunks_to_vector_db, ensure_collection
from app.config import settings


def batchify(iterable, batch_size: int):
    for i in range(0, len(iterable), batch_size):
        yield iterable[i : i + batch_size]


async def ingest_pdf_bytes(pdf_bytes: bytes, doc_name: str) -> int:
    """
    Extract text from PDF bytes, chunk with fixed size (chars), embed, and upsert to Qdrant.
    Returns the number of chunks indexed.
    """
    text = extract_text(BytesIO(pdf_bytes))
    if not text or not text.strip():
        return 0

    splitter = FixedSizeCharSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    doc_chunks = splitter.split(text)
    doc_id = str(uuid4())[:8]
    chunks = []
    for chunk_idx, chunk_text in enumerate(doc_chunks):
        chunks.append({
            "id": uuid4(),
            "chunk_id": f"{doc_id}:{chunk_idx + 1:04}",
            "text": chunk_text,
            "doc_name": doc_name,
            "vector": None,
        })

    if not chunks:
        return 0

    # Embed in batches
    vectors = []
    for batch in batchify(chunks, batch_size=64):
        batch_vectors = await get_embeddings([c["text"] for c in batch])
        vectors.extend(batch_vectors)
    for chunk, vector in zip(chunks, vectors):
        chunk["vector"] = vector

    ensure_collection()
    await add_chunks_to_vector_db(chunks)
    return len(chunks)
