"""
ingest.py — Parse all PDFs in DATA_DIR, chunk the text, embed with
sentence-transformers, and persist to ChromaDB.

Run directly to (re)build the index:
    python ingest.py
"""

import sys
import fitz  # PyMuPDF
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer

from config import (
    DATA_DIR,
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    MIN_CHUNK_LENGTH,
)


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping fixed-size character chunks."""
    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start : start + CHUNK_SIZE]
        if len(chunk.strip()) >= MIN_CHUNK_LENGTH:
            chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def ingest_pdfs(data_dir: Path = DATA_DIR) -> None:
    print(f"Loading embedding model: {EMBEDDING_MODEL}", file=sys.stderr)
    model = SentenceTransformer(EMBEDDING_MODEL)

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Skip the assignment PDF itself — only ingest the data/ subdirectories
    pdf_files = [
        p for p in data_dir.rglob("*.pdf")
        if p.parent != Path(".")  # exclude root-level PDFs
    ]

    print(f"Found {len(pdf_files)} PDF files to ingest", file=sys.stderr)

    for pdf_path in pdf_files:
        print(f"  Processing: {pdf_path.name}", file=sys.stderr)
        try:
            doc = fitz.open(str(pdf_path))
        except Exception as e:
            print(f"  ERROR opening {pdf_path.name}: {e}", file=sys.stderr)
            continue

        ids, documents, embeddings, metadatas = [], [], [], []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if not text.strip():
                continue

            for chunk_idx, chunk in enumerate(chunk_text(text)):
                doc_id = f"{pdf_path.stem}_p{page_num + 1}_c{chunk_idx}"
                ids.append(doc_id)
                documents.append(chunk)
                metadatas.append({
                    "source": pdf_path.name,
                    "page": page_num + 1,
                    "chunk": chunk_idx,
                })

        doc.close()

        if not ids:
            continue

        # Batch encode for efficiency
        batch_embeddings = model.encode(documents, batch_size=64, show_progress_bar=False)

        # Upsert in batches of 500 to stay within ChromaDB limits
        batch_size = 500
        for i in range(0, len(ids), batch_size):
            collection.upsert(
                ids=ids[i : i + batch_size],
                documents=documents[i : i + batch_size],
                embeddings=[e.tolist() for e in batch_embeddings[i : i + batch_size]],
                metadatas=metadatas[i : i + batch_size],
            )

    total = collection.count()
    print(f"Ingestion complete — {total} chunks stored in ChromaDB", file=sys.stderr)


if __name__ == "__main__":
    ingest_pdfs()
