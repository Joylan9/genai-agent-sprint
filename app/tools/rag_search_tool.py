# app/services/rag_search_tool.py
import logging
from typing import List, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class RAGSearchTool:
    """
    RAG search tool that queries the local vector store and returns
    top-k document chunks and similarity scores.

    Initialized with:
      - embedding_service: exposes `encode(list[str]) -> list[float] | np.ndarray`
      - retriever: exposes `vector_store.documents` and `vector_store.document_embeddings`
    """

    def __init__(self, embedding_service, retriever):
        self.embedding_service = embedding_service
        self.retriever = retriever

    # ------------------------
    # Internal helpers
    # ------------------------
    def _get_documents_and_embeddings(self) -> Tuple[List[str], np.ndarray]:
        """
        Returns (documents, document_embeddings) where document_embeddings is np.ndarray (N, dim).
        """
        vs = getattr(self.retriever, "vector_store", self.retriever)

        docs = getattr(vs, "documents", None)
        embeds = getattr(vs, "document_embeddings", None)

        if docs is None or embeds is None:
            raise RuntimeError(
                "Could not find documents/document_embeddings on retriever.vector_store. "
                "Ensure vector_store exposes 'documents' (List[str]) and 'document_embeddings' (np.ndarray or list)."
            )

        doc_embeddings = np.asarray(embeds, dtype=np.float32)
        if doc_embeddings.ndim != 2:
            raise RuntimeError(f"document_embeddings must be 2D; got shape {doc_embeddings.shape}")

        return list(docs), doc_embeddings

    def _cosine_similarities(self, qvec: np.ndarray, doc_embeddings: np.ndarray) -> np.ndarray:
        # qvec shape (dim,) ; doc_embeddings shape (N, dim)
        if qvec.ndim == 2 and qvec.shape[0] == 1:
            qvec = qvec[0]

        doc_norms = np.linalg.norm(doc_embeddings, axis=1)
        q_norm = np.linalg.norm(qvec)

        # numeric safety
        doc_norms = np.where(doc_norms == 0.0, 1e-8, doc_norms)
        q_norm = 1e-8 if q_norm == 0.0 else q_norm

        sims = np.dot(doc_embeddings, qvec) / (doc_norms * q_norm)
        return sims

    # ------------------------
    # Public API
    # ------------------------
    def search_with_score(self, query: str, top_k: int = 1) -> Tuple[List[str], List[float]]:
        """
        Returns (top_documents: List[str], top_scores: List[float]) ALWAYS.
        If top_k == 1 returns lists with single element.
        """
        docs, doc_embeddings = self._get_documents_and_embeddings()

        # embed the query (embedding_service may return list or numpy array)
        query_emb = self.embedding_service.encode([query])
        query_emb = np.asarray(query_emb, dtype=np.float32)

        if query_emb.ndim == 2 and query_emb.shape[0] == 1:
            qvec = query_emb[0]
        else:
            qvec = np.squeeze(query_emb)

        sims = self._cosine_similarities(qvec, doc_embeddings)

        top_k = max(1, int(top_k))
        top_indices = np.argsort(sims)[-top_k:][::-1]

        top_docs = [docs[i] for i in top_indices]
        top_scores = [float(sims[i]) for i in top_indices]

        return top_docs, top_scores

    def search(self, query: str, top_k: int = 3, separator: str = "\n\n") -> str:
        """
        Backwards-compatible convenience method: return concatenated top_k segments.
        """
        try:
            top_docs, top_scores = self.search_with_score(query, top_k=top_k)
        except Exception as e:
            logger.exception("RAG search failed: %s", e)
            return "RAG search failed: " + str(e)

        segments = [f"[score={s:.4f}]\n{d}" for d, s in zip(top_docs, top_scores)]
        return separator.join(segments)
