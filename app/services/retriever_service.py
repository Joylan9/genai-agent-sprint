import numpy as np


class RetrieverService:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def _cosine_similarity(self, vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def retrieve(self, query_embedding, top_k=2):
        similarities = [
            self._cosine_similarity(query_embedding, doc_embedding)
            for doc_embedding in self.vector_store.embeddings
        ]

        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [self.vector_store.documents[i] for i in top_indices]
