from pathlib import Path

# Paths
DATA_DIR = Path("data")
CHROMA_DIR = Path(".chroma")

# ChromaDB
COLLECTION_NAME = "documents"

# Embedding model (runs locally, no API key needed)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Ollama model for answer synthesis (must be pulled first: ollama pull llama3.2)
OLLAMA_MODEL = "llama3.2"

# Chunking
CHUNK_SIZE = 1000       # characters per chunk
CHUNK_OVERLAP = 200     # overlap between consecutive chunks
MIN_CHUNK_LENGTH = 50   # skip chunks shorter than this (page numbers, headers, etc.)

# Retrieval
TOP_K = 5               # number of chunks to retrieve per query
