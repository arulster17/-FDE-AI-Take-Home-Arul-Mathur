# Document Q&A MCP Server

An MCP (Model Context Protocol) server that lets any MCP-compatible AI agent ask natural language questions over a collection of PDF documents and receive grounded answers with source citations.

Built as part of the Nexla Forward Deployed Engineer - AI take-home assignment.

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
server.py  (FastMCP - stdio transport)
  └── query_documents(question)
        ├── retriever.py
        │     ├── embed question (SentenceTransformers)
        │     └── cosine similarity search → top-5 chunks from ChromaDB
        └── llm.py
              ├── build prompt with retrieved chunks + citations
              ├── Ollama (local LLM - llama3.2)
              └── return answer with [Source: file, Page N] inline citations
```

**Key design decisions:**

- **Fully local, no API keys.** `all-MiniLM-L6-v2` embeds on CPU via sentence-transformers; Ollama runs the LLM locally. Zero cloud dependencies.
- **Persist once, serve many.** ChromaDB writes to `.chroma/` on disk. The server checks for an existing index at startup; ingestion only runs when needed.
- **Page-level metadata.** Every chunk carries its source filename and page number, so citations are always traceable to a specific location.
- **One tool, one job.** `query_documents` is the single exposed tool - scoped exactly to what the assignment requires.

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

### 4. Connect an MCP client

The server works with any MCP-compatible client via stdio transport. How you start it depends on your client - most (Claude Code, Claude Desktop) launch it automatically from the registered command.

Example using Claude Code:

```bash
claude mcp add document-qa python "/absolute/path/to/server.py"
```

Then start a new Claude Code session from the project directory.

On first run the server will automatically ingest all PDFs in `data/` and build the ChromaDB index. Subsequent starts reuse the persisted index.

Ollama must be running before starting the server (`ollama serve` if it isn't already).

---

## Tool Documentation

### `query_documents`

Ask a natural language question. The server retrieves the most relevant chunks from the indexed PDFs and uses Ollama to synthesise a grounded answer.

| | |
|---|---|
| **Input** | `question: str` - any natural language question |
| **Output** | Answer with inline `[Source: filename, Page N]` citations |
| **Multi-doc** | Retrieval searches across all indexed documents simultaneously |

**Example queries:**
- `"What is IBM's strategy for hybrid cloud and AI as described in their 2020 annual report?"`
- `"How does the DeClarE system use web evidence to detect fake news?"`
- `"How did ExxonMobil and IBM each describe the impact of COVID-19 on their business in 2020?"`

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

### Tools used

- **Claude Code** (Anthropic's CLI) - primary AI coding assistant throughout this project, running inside VS Code.

### How the AI was directed

<!-- NOTE: Fill this in with your own words after completing the project. Here are some prompts to guide you:
  - How did the conversation start? (e.g. shared the assignment PDF, asked for a breakdown, then agreed on a plan)
  - How did you move from architecture discussion to code generation?
  - Did you prompt it with constraints ("use only one API key", "keep it simple") or let it propose freely?
  - What did a typical back-and-forth look like - was it one shot or iterative?
-->

### What worked well

<!-- NOTE: Fill this in. Some things worth mentioning:
  - How fast the scaffolding went once the architecture was agreed on
  - Whether the AI caught edge cases you hadn't thought of (e.g. stdout/stderr separation for MCP stdio, batch encoding for performance)
  - Any places where the generated code was production-quality on the first pass
-->

### Where I overrode or corrected the AI

<!-- NOTE: Be honest here - this section is worth points. Examples to consider:
  - Any design choices you changed after seeing the first draft
  - Bugs or logic errors you caught before running
  - Places where the AI was too clever or too verbose and you simplified it
  - Cases where you made a different technology tradeoff than what was suggested
-->

### Overall take on AI tooling for forward-deployed engineering

<!-- NOTE: Write your genuine view. Some angles to consider:
  - The speed advantage is real - scaffolding a working multi-file Python project in a single session is dramatically faster
  - But the FDE value-add is in the *decisions*: which stack, what trade-offs, what the customer actually needs vs. what's technically interesting
  - AI tools compress implementation time; they don't replace the judgment about *what* to build
  - For customer-facing work, the README and the reasoning behind choices matter as much as the code - the AI can draft, but the engineer has to own it
  - How would you use these tools differently when working directly with a customer vs. solo?
-->
