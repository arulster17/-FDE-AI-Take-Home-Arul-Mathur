"""
retriever.py — Embed a query and fetch the top-k most relevant chunks
from ChromaDB using cosine similarity.
"""

import chromadb
from sentence_transformers import SentenceTransformer

from config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL, TOP_K

# Module-level singletons — loaded once, reused across tool calls
_model: SentenceTransformer | None = None
_collection = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    """
    Return the top-k chunks most relevant to `query`.

    Each result dict contains:
        text    — the raw chunk text
        source  — filename of the source PDF
        page    — page number within that PDF
        score   — cosine similarity (higher = more relevant)
    """
    model = _get_model()
    collection = _get_collection()

    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for text, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text": text,
            "source": meta["source"],
            "page": meta["page"],
            "score": round(1 - distance, 4),  # cosine distance → similarity
        })

    return chunks
