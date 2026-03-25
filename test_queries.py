"""
test_queries.py — Run a set of sample questions against the indexed documents
and print formatted markdown suitable for pasting into examples/interaction_log.md.

Usage:
    python test_queries.py
"""

from retriever import retrieve
from llm import answer

QUERIES = [
    # Single-document questions
    "What task does the Misra et al. paper address and what is their proposed approach for executing instructions in 3D environments?",
    "How does the NAACL 2019 paper use dynamic span graphs for information extraction?",
    "What does the document say about Russia stealing Ukrainian grain and the US response?",
    "What are the key topics covered in the Law Library of Congress report on Turkey's presidential decrees?",
    "How did Bank of America perform financially in 2020 and what were the main challenges they faced?",
    # Multi-document question
    "How do the Misra et al. and Luan et al. papers each handle the relationship between language and structured output?",
]


def run():
    for i, question in enumerate(QUERIES, start=1):
        print(f"## Query {i}\n")
        print(f"**Question:** {question}\n")
        chunks = retrieve(question)
        if not chunks:
            print("**Answer:** No relevant content found.\n")
        else:
            result = answer(question, chunks)
            print(f"**Answer:**\n\n{result}\n")
        print("---\n")


if __name__ == "__main__":
    run()
