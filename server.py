"""
server.py - FastMCP server exposing document Q&A over the provided PDFs.

Start the server (stdio transport, compatible with Claude Desktop / Claude Code):
    python server.py

On first run the server will automatically ingest all PDFs in data/ before
accepting requests.  Subsequent runs reuse the persisted ChromaDB index.
"""

import sys
import chromadb
from fastmcp import FastMCP

from config import CHROMA_DIR, COLLECTION_NAME
from retriever import retrieve
from llm import answer


# ---------------------------------------------------------------------------
# Startup: ensure the vector index exists
# ---------------------------------------------------------------------------

def _index_ready() -> bool:
    try:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        col = client.get_collection(COLLECTION_NAME)
        return col.count() > 0
    except Exception:
        return False


def _ensure_index() -> None:
    if _index_ready():
        print("ChromaDB index found - skipping ingestion.", file=sys.stderr)
        return
    print("No index found - running ingestion (this may take a few minutes)…", file=sys.stderr)
    from ingest import ingest_pdfs
    ingest_pdfs()


# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

mcp = FastMCP("Document Q&A Server")


@mcp.tool()
def query_documents(question: str) -> str:
    """
    Answer a natural language question using the indexed PDF document collection.

    Returns a grounded answer with inline citations of the form
    [Source: <filename>, Page <n>] for every claim.
    """
    chunks = retrieve(question)
    if not chunks:
        return (
            "No relevant content found for that question. "
            "Try rephrasing or asking about a different topic."
        )
    return answer(question, chunks)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    _ensure_index()
    mcp.run()
