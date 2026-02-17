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

        document = LongTermMemoryDocument(
            session_id=session_id,
            text=text,
            embedding=embedding.tolist()
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

        query_embedding = np.array(
            self.embedding_service.embed_text(query)
        )

        cursor = self.db.long_term_memory.find(
            {"session_id": session_id}
        )

        documents = await cursor.to_list(length=100)

        scored = []

        for doc in documents:
            stored_embedding = np.array(doc["embedding"])

            similarity = self.cosine_similarity(
                query_embedding,
                stored_embedding
            )

            scored.append((similarity, doc))

        scored.sort(key=lambda x: x[0], reverse=True)

        return [doc for _, doc in scored[:top_k]]

    @staticmethod
    def cosine_similarity(vec1, vec2):
        if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
            return 0.0

        return float(
            np.dot(vec1, vec2)
            / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        )
