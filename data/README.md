# Data Directory

This directory contains the knowledge base for the RAG (Retrieval Augmented Generation) system.

- `docs/`: Markdown files containing technical documentation.
- `sample.txt`: Legacy sample file used for initial testing.
- `vector_store.pkl`: Generated serialized vector store and index.

To rebuild the vector store after adding new documents to `docs/`, run:
```bash
python scripts/build_vector_store.py
```
