# Example Interaction Log

Sample queries run against the live server after ingesting the following 5 documents:

| File | Description |
|---|---|
| `NYSE_BAC_2020.pdf` | Bank of America 2020 Annual Report |
| `D18-1287.pdf` | EMNLP 2018 — "Mapping Instructions to Actions in 3D Environments with Visual Goal Prediction" |
| `N19-1308.pdf` | NAACL 2019 — "A General Framework for Information Extraction using Dynamic Span Graphs" |
| `20220606.pdf` | News article (June 2022) on Russia stealing Ukrainian grain |
| `2022666100.pdf` | Law Library of Congress — Turkey: Presidential Decrees (January 2022) |

---

## Query 1

**Tool:** `query_documents`
**Question:** `"What task does the Misra et al. paper address and what is their proposed approach for executing instructions in 3D environments?"`

**Answer:**

> _[run `python test_queries.py` and paste output here]_

---

## Query 2

**Tool:** `query_documents`
**Question:** `"How does the NAACL 2019 paper use dynamic span graphs for information extraction?"`

**Answer:**

> _[run `python test_queries.py` and paste output here]_

---

## Query 3

**Tool:** `query_documents`
**Question:** `"What does the document say about Russia stealing Ukrainian grain and the US response?"`

**Answer:**

> _[run `python test_queries.py` and paste output here]_

---

## Query 4

**Tool:** `query_documents`
**Question:** `"What are the key topics covered in the Law Library of Congress report on Turkey's presidential decrees?"`

**Answer:**

> _[run `python test_queries.py` and paste output here]_

---

## Query 5

**Tool:** `query_documents`
**Question:** `"How did Bank of America perform financially in 2020 and what were the main challenges they faced?"`

**Answer:**

> _[run `python test_queries.py` and paste output here]_

---

## Query 6 — Multi-document

**Tool:** `query_documents`
**Question:** `"How do the Misra et al. and Luan et al. papers each handle the relationship between language and structured output?"`

**Answer:**

> _[run `python test_queries.py` and paste output here]_

