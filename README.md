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

### Which AI coding tool(s) you used and how

Claude Code was the primary AI coding assistant throughout this project, which I used inside VS Code and occasionally through the terminal. I used this tool in a conversational session, and directed it step-by-step.

### How you prompted or directed the AI — what worked, what did not

I started by feeding Claude the assignment PDF and asking for a breakdown before touching any code. I then asked Claude to propose a file structure and tech stack, then reviewed and approved the plan. I also decided on additional constraints, such as avoiding API keys for ease of use, and sticking close to the assignment to keep Claude focused on the correct tasks. Once I was satisfied with the architecture and planning, I let the agent do a first pass of an implementation. From there, there was an iterative process of reviewing the code, asking questions or correcting the agent when needed, then testing again. I found that Claude worked best when I gave it clear constraints and instructions, rather than just letting it work freely. 

### Where you leaned on the AI vs. where you overrode or corrected it

After agreeing on the overall architecture and stack, Claude was able to generate all files quickly with good separation of concerns, so I didn't need to do much restructuring. The core RAG pipeline worked very well off the bat, and the generated code was readable and high enough quality that I could review and push it without much cleanup. I especially leaned on the AI to work with tools where I was not familiar with the documentation or had never used before.

There were several times I had to override or course-correct the AI. Claude often tried to add unnecessary features, such as an additional list_documents tool or suppressing warnings by setting OS environment variables. The agent would also try to overengineer the tool itself by adding unnecessary parameters on the MCP server. Generating example interaction logs also needed several rounds of iteration, as there were many flaws in the examples/tests it tried to generate that had to be ironed out. I also overrode several of Claude's original tech stack decisions; most importantly, it initially proposed using the Anthropic API for the LLM, which I replaced with Ollama to eliminate the API key requirement. Finally, there would be several times where artifacts from previous versions of the tool would exist in the documentation or setup files, which I would have to catch and make sure Claude kept updated.

### Overall take on AI tooling for forward-deployed engineering

I think that the additional speed gained by using these AI tools was incredible; building a RAG and MCP system would have taken far longer without AI assistance, but with Claude it could be done in a single session. However, I felt that without very clear directions and a solid human plan, the agent could get off track and add extraneous or even incorrect features. I think that in a real-life scenario, this "overeagerness" to add additional functionality would actually do more harm than good, so I believe when using Claude and similar tools, one must treat them as implementers rather than decision-makers. However, when a human carefully defines the scope and architecture of the project and reviews the agent outputs carefully, these tools can produce high-quality code very quickly.