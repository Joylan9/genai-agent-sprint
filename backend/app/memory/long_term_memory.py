"""
Long-term semantic memory service.
Stores and retrieves vectorized interaction history.
"""

from typing import List, Dict
from app.memory.database import MongoDB
from app.memory.models import LongTermMemoryDocument
from app.services.embedding_service import EmbeddingService
import numpy as np


class LongTermMemory:

    def __init__(self):
        self.db = MongoDB.connect()
        self.embedding_service = EmbeddingService()

    async def store_interaction(
        self,
        session_id: str,
        text: str
    ):
        embedding = self.embedding_service.embed_text(text)

        # Normalize embedding to a plain Python list safely
        if hasattr(embedding, "tolist"):
            emb_list = embedding.tolist()
        elif isinstance(embedding, list):
            emb_list = embedding
        else:
            # Fallback: convert iterable to list
            emb_list = list(embedding)

        document = LongTermMemoryDocument(
            session_id=session_id,
            text=text,
            embedding=emb_list
        )

        await self.db.long_term_memory.insert_one(
            document.model_dump()
        )

    async def retrieve_relevant(
        self,
        session_id: str,
        query: str,
        top_k: int = 3
    ) -> List[Dict]:

        # Ensure query embedding is a numpy array
        query_embedding = np.array(self.embedding_service.embed_text(query))

        cursor = self.db.long_term_memory.find(
            {"session_id": session_id}
        )

        documents = await cursor.to_list(length=100)

        scored = []

        for doc in documents:
            stored_vec = doc.get("embedding", [])
            # Convert stored embedding to numpy array safely
            try:
                stored_embedding = np.array(stored_vec)
            except Exception:
                stored_embedding = np.array([])

            similarity = self.cosine_similarity(
                query_embedding,
                stored_embedding
            )

            scored.append((similarity, doc))

        scored.sort(key=lambda x: x[0], reverse=True)

        return [doc for _, doc in scored[:top_k]]

    @staticmethod
    def cosine_similarity(vec1, vec2):
        try:
            if vec1 is None or vec2 is None:
                return 0.0
            if len(vec1) == 0 or len(vec2) == 0:
                return 0.0
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return float(np.dot(vec1, vec2) / (norm1 * norm2))
        except Exception:
            return 0.0
