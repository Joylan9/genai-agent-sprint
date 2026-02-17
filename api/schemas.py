"""
api/schemas.py
Pydantic request/response models for the AI Agent API.
"""

from pydantic import BaseModel, Field
from typing import Optional


class AgentRequest(BaseModel):
    session_id: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Unique session identifier for conversation tracking."
    )

    goal: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User goal or complex query for the AI agent."
    )


class AgentResponse(BaseModel):
    result: str
    request_id: Optional[str] = None
