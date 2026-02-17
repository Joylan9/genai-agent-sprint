"""
Memory document models.
Defines structure for MongoDB documents.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
from uuid import uuid4


# ----------------------------
# Conversation Message Model
# ----------------------------
class ConversationMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    role: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ----------------------------
# Long-Term Memory Model
# ----------------------------
class LongTermMemoryDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    text: str
    embedding: List[float]
    created_at: datetime = Field(default_factory=datetime.utcnow)
