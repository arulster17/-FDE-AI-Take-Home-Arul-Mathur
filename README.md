# Document Q&A MCP Server

An MCP (Model Context Protocol) server that lets any MCP-compatible AI agent ask natural language questions over a collection of PDF documents and receive grounded answers with source citations.

Built as part of the Nexla Forward Deployed Engineer – AI take-home assignment.

---

## Architecture Overview

```
data/ (PDF documents)
      │
      ▼
ingest.py
  ├── PyMuPDF     → extract text page-by-page
  ├── chunk_text  → split into overlapping 1000-char chunks
  ├── SentenceTransformers (all-MiniLM-L6-v2) → embed each chunk locally
  └── ChromaDB    → persist vectors + metadata to .chroma/

                  (one-time, or re-run to refresh)

At query time:
      │
      ▼
server.py  (FastMCP — stdio transport)
  └── query_documents(question)
        ├── retriever.py
        │     ├── embed question (SentenceTransformers)
        │     └── cosine similarity search → top-5 chunks from ChromaDB
        └── llm.py
              ├── build prompt with retrieved chunks + citations
              ├── Ollama (local LLM — llama3.2)
              └── return answer with [Source: file, Page N] inline citations
```

**Key design decisions:**

- **Fully local, no API keys.** `all-MiniLM-L6-v2` embeds on CPU via sentence-transformers; Ollama runs the LLM locally. Zero cloud dependencies.
- **Persist once, serve many.** ChromaDB writes to `.chroma/` on disk. The server checks for an existing index at startup; ingestion only runs when needed.
- **Page-level metadata.** Every chunk carries its source filename and page number, so citations are always traceable to a specific location.
- **One tool, one job.** `query_documents` is the single exposed tool — scoped exactly to what the assignment requires.

---

## Setup Instructions

### 1. Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed and running locally

### 2. Pull the local model

```bash
ollama pull llama3.2
```

### 3. Clone and install dependencies

```bash
git clone <repo-url>
cd <repo-dir>
pip install -r requirements.txt
```

### 4. (Optional) Pre-build the index

The server builds the index automatically on first run, but you can do it explicitly:

```bash
python ingest.py
```

This walks `data/`, parses every PDF with PyMuPDF, chunks the text, embeds it with `all-MiniLM-L6-v2`, and stores everything in `.chroma/`. Subsequent server starts reuse the persisted index.

### 5. Run the MCP server

```bash
python server.py
```

The server speaks the MCP stdio protocol and is ready to be connected to any MCP-compatible client (Claude Desktop, Claude Code, etc.).

### 6. Connect via Claude Desktop (example)

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "document-qa": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

Ollama must be running locally (`ollama serve`) before starting the server.

---

## Tool Documentation

### `query_documents`

Ask a natural language question. The server retrieves the most relevant chunks from the indexed PDFs and uses Ollama to synthesise a grounded answer.

| | |
|---|---|
| **Input** | `question: str` — any natural language question |
| **Output** | Answer with inline `[Source: filename, Page N]` citations |
| **Multi-doc** | Retrieval searches across all indexed documents simultaneously |

**Example queries:**
- `"What is the main contribution of the EMNLP 2018 paper on mapping instructions to actions?"`
- `"How did Bank of America perform financially in 2020?"`
- `"What do the two NLP research papers have in common in their technical approach?"`

---

## Configuration

All tuneable constants live in `config.py`:

| Variable | Default | Description |
|---|---|---|
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence-transformers model |
| `OLLAMA_MODEL` | `llama3.2` | Ollama model for answer synthesis |
| `CHUNK_SIZE` | `1000` | Characters per chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between consecutive chunks |
| `TOP_K` | `5` | Chunks retrieved per query |

---

## Example Interactions

See [examples/interaction_log.md](examples/interaction_log.md) for sample queries and responses.

---









## Vibe Coding Section
TODO