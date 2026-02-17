"""
Short-term conversation memory service.
Handles recent conversation retrieval and storage.
"""

from typing import List, Dict
from app.memory.database import MongoDB
from app.memory.models import ConversationMessage


class ShortTermMemory:

    def __init__(self):
        self.db = MongoDB.connect()

    async def save_message(
        self,
        session_id: str,
        role: str,
        content: str
    ):
        message = ConversationMessage(
            session_id=session_id,
            role=role,
            content=content
        )

        await self.db.conversations.insert_one(
            message.model_dump()
        )

    async def get_recent_messages(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict]:

        cursor = (
            self.db.conversations
            .find({"session_id": session_id})
            .sort("created_at", -1)
            .limit(limit)
        )

        messages = await cursor.to_list(length=limit)

        messages.reverse()

        return messages
