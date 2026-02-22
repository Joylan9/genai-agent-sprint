# Retrieval Augmented Generation (RAG)

Hybrid search strategy:
- Dense Retrieval: Semantic search using sentence-transformers (all-MiniLM-L6-v2).
- Metadata Filtering: Narrowing down results by tags or source.
- Confidence Scoring: Cosine similarity thresholding for relevance.
- Knowledge Source: Replicated vector store for fast local retrieval.
