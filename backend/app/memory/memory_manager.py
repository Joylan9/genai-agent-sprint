"""
Unified Memory Manager.
Coordinates short-term and long-term memory layers.
"""

from typing import List, Dict
from app.memory.short_term_memory import ShortTermMemory
from app.memory.long_term_memory import LongTermMemory


class MemoryManager:

    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()

    # ----------------------------
    # Save Interaction
    # ----------------------------
    async def save_interaction(
        self,
        session_id: str,
        user_message: str,
        assistant_message: str
    ):
        # Save short-term messages
        await self.short_term.save_message(
            session_id=session_id,
            role="user",
            content=user_message
        )

        await self.short_term.save_message(
            session_id=session_id,
            role="assistant",
            content=assistant_message
        )

        # Store combined interaction in long-term memory
        combined_text = f"User: {user_message}\nAssistant: {assistant_message}"

        await self.long_term.store_interaction(
            session_id=session_id,
            text=combined_text
        )

    # ----------------------------
    # Retrieve Context
    # ----------------------------
    async def retrieve_context(
        self,
        session_id: str,
        query: str,
        recent_limit: int = 5,
        semantic_top_k: int = 3
    ) -> Dict:

        recent_messages = await self.short_term.get_recent_messages(
            session_id=session_id,
            limit=recent_limit
        )

        relevant_memory = await self.long_term.retrieve_relevant(
            session_id=session_id,
            query=query,
            top_k=semantic_top_k
        )

        return {
            "recent_messages": recent_messages,
            "relevant_memory": relevant_memory
        }
