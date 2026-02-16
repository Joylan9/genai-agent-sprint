from pydantic import BaseModel, Field
from typing import Optional


class AgentRequest(BaseModel):
    goal: str = Field(..., min_length=1, max_length=5000)


class AgentResponse(BaseModel):
    result: str
    request_id: Optional[str]
