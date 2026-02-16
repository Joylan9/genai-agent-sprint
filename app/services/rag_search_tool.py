# app/services/rag_search_tool.py
import logging
from typing import List, Tuple, Union, Optional

import numpy as np

logger = logging.getLogger(__name__)


class RAGSearchTool:
    """
    RAG search tool that queries the local vector store and returns
    top-k document chunks and similarity scores.

    Expected to be initialized with:
      - embedding_service: object exposing `encode([texts]) -> np.ndarray`
      - retriever: object exposing access to the vector store documents and embeddings.
        This implementation tries to support common shapes:
          retriever.vector_store.documents (List[str])
          retriever.vector_store.document_embeddings (np.ndarray or List[List[float]])
    """

    def __init__(self, embedding_service, retriever):
        self.embedding_service = embedding_service
        self.retriever = retriever

    # ------------------------
    # Internal helpers
    # ------------------------
    def _get_documents_and_embeddings(self) -> Tuple[List[str], np.ndarray]:
        """
        Attempt to extract documents and embeddings from the retriever/vector_store.
        Raises RuntimeError with helpful message if not available.
        """
        vs = None
        # common location: retriever.vector_store
        if hasattr(self.retriever, "vector_store"):
            vs = getattr(self.retriever, "vector_store")
        else:
            # fallback: retriever itself may expose documents & embeddings
            vs = self.retriever

        docs = getattr(vs, "documents", None)
        embeddings = getattr(vs, "document_embeddings", None)

        if docs is None or embeddings is None:
            raise RuntimeError(
                "Could not find documents/document_embeddings on retriever.vector_store. "
                "Ensure your vector_store exposes 'documents' (List[str]) and "
                "'document_embeddings' (np.ndarray or list of lists)."
            )

        # normalize embeddings to numpy array (dtype=float32)
        embeddings = np.asarray(embeddings, dtype=np.float32)

        if embeddings.ndim != 2:
            raise RuntimeError(
                f"document_embeddings must be 2-dimensional (num_docs x dim). Got shape {embeddings.shape}"
            )

        return docs, embeddings

    def _cosine_similarities(self, query_vec: np.ndarray, doc_embeddings: np.ndarray) -> np.ndarray:
        """
        Vectorized cosine similarity between query_vec (dim,) and doc_embeddings (N, dim)
        Returns array shape (N,)
        """
        # ensure shapes
        if query_vec.ndim == 2 and query_vec.shape[0] == 1:
            query_vec = query_vec[0]

        # small numeric safety
        doc_norms = np.linalg.norm(doc_embeddings, axis=1)
        query_norm = np.linalg.norm(query_vec)

        # avoid division by zero
        doc_norms = np.where(doc_norms == 0.0, 1e-8, doc_norms)
        if query_norm == 0.0:
            query_norm = 1e-8

        sims = np.dot(doc_embeddings, query_vec) / (doc_norms * query_norm)
        return sims

    # ------------------------
    # Public API
    # ------------------------
    def search_with_score(self, query: str, top_k: int = 1) -> Union[Tuple[str, float], Tuple[List[str], List[float]]]:
        """
        Compute embeddings for the query, score against the vector store, and return the top_k documents
        and their similarity scores.

        If top_k == 1, returns (top_document: str, top_score: float).
        If top_k > 1, returns (top_documents: List[str], top_scores: List[float]).
        """
        docs, doc_embeddings = self._get_documents_and_embeddings()

        # embed the query
        query_emb = self.embedding_service.encode([query])
        if isinstance(query_emb, list):
            query_emb = np.asarray(query_emb, dtype=np.float32)

        if query_emb.ndim == 2 and query_emb.shape[0] == 1:
            qvec = query_emb[0]
        else:
            qvec = np.squeeze(query_emb)

        sims = self._cosine_similarities(qvec, doc_embeddings)

        # get top_k indices (descending)
        top_k = max(1, int(top_k))
        top_indices = np.argsort(sims)[-top_k:][::-1]
        top_scores = [float(sims[i]) for i in top_indices]
        top_docs = [docs[i] for i in top_indices]

        if top_k == 1:
            return top_docs[0], top_scores[0]

        return top_docs, top_scores

    def search(self, query: str, top_k: int = 3, separator: str = "\n\n") -> str:
        """
        Convenience method: returns top_k contexts concatenated as a single string.
        Keeps backwards compatibility with previous 'search' API.
        """
        try:
            top_docs, top_scores = self.search_with_score(query, top_k=top_k)
            # if top_k == 1, search_with_score returns single doc/score; normalize
            if isinstance(top_docs, str):
                top_docs = [top_docs]
                top_scores = [top_scores]
        except Exception as e:
            logger.exception("RAG search failed: %s", e)
            return "RAG search failed: " + str(e)

        segments = []
        for idx, doc in enumerate(top_docs):
            score = top_scores[idx]
            segments.append(f"[score={score:.4f}]\n{doc}")

        return separator.join(segments)
