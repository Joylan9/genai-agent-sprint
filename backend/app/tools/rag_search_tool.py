# app/tools/rag_search_tool.py

import logging
from typing import List, Tuple, Dict, Any
import numpy as np

from app.tools.tools import BaseTool

logger = logging.getLogger(__name__)


class RAGSearchTool(BaseTool):

    name = "rag_search"

    def __init__(self, embedding_service, retriever):
        self.embedding_service = embedding_service
        self.retriever = retriever

    # ------------------------
    # Internal helpers
    # ------------------------
    def _get_documents_and_embeddings(self) -> Tuple[List[str], np.ndarray]:
        vs = getattr(self.retriever, "vector_store", self.retriever)

        docs = getattr(vs, "documents", None)
        embeds = getattr(vs, "document_embeddings", None)

        if docs is None or embeds is None:
            raise RuntimeError(
                "Could not find documents/document_embeddings on retriever.vector_store."
            )

        doc_embeddings = np.asarray(embeds, dtype=np.float32)
        if doc_embeddings.ndim != 2:
            raise RuntimeError(
                f"document_embeddings must be 2D; got shape {doc_embeddings.shape}"
            )

        return list(docs), doc_embeddings

    def _cosine_similarities(
        self, qvec: np.ndarray, doc_embeddings: np.ndarray
    ) -> np.ndarray:

        if qvec.ndim == 2 and qvec.shape[0] == 1:
            qvec = qvec[0]

        doc_norms = np.linalg.norm(doc_embeddings, axis=1)
        q_norm = np.linalg.norm(qvec)

        doc_norms = np.where(doc_norms == 0.0, 1e-8, doc_norms)
        q_norm = 1e-8 if q_norm == 0.0 else q_norm

        sims = np.dot(doc_embeddings, qvec) / (doc_norms * q_norm)
        return sims

    # ------------------------
    # Public API
    # ------------------------
    def search_with_score(self, query: str, top_k: int = 1):
        docs, doc_embeddings = self._get_documents_and_embeddings()

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

    # ------------------------
    # Enterprise Execute Wrapper
    # ------------------------
    def execute(self, step: Dict[str, Any]) -> Dict[str, Any]:

        raw_query = step.get("query")

        if not isinstance(raw_query, str) or not raw_query.strip():
            return {
                "status": "error",
                "data": None,
                "metadata": {"error": "Invalid or missing query string."}
            }

        query: str = raw_query.strip()

        try:
            docs, scores = self.search_with_score(query, top_k=3)

            max_score = max(scores) if scores else 0.0
            combined = "\n\n".join(docs)

            return {
                "status": "success",
                "data": combined,
                "metadata": {
                    "similarity": max_score
                }
            }

        except Exception as e:
            logger.exception("RAG execution failed")
            return {
                "status": "error",
                "data": None,
                "metadata": {"error": str(e)}
            }
