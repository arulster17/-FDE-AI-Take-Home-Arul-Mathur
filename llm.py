"""
llm.py - Send retrieved chunks + the user's question to a local Ollama model
and return a grounded answer with inline source citations.
"""

import ollama
from config import OLLAMA_MODEL


def answer(question: str, chunks: list[dict]) -> str:
    """
    Synthesise an answer from `chunks` using a local Ollama model.

    Each chunk dict must have: text, source, page.
    Returns a grounded answer with inline [Source: filename, Page N] citations.
    """
    context_blocks = []
    for chunk in chunks:
        context_blocks.append(
            f"Source: {chunk['source']}, Page {chunk['page']}\n{chunk['text'].strip()}"
        )
    context = "\n\n---\n\n".join(context_blocks)

    prompt = f"""You are a document Q&A assistant. Use only the context below to answer the question.

Rules:
- Cite every factual claim with the notation [Source: <filename>, Page <n>].
- If the context spans multiple documents, synthesise across all of them.
- If the context does not contain enough information, say so clearly instead of guessing.
- Keep the answer concise and directly responsive to the question.

Context:
{context}

Question: {question}

Answer:"""

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.message.content.strip()
