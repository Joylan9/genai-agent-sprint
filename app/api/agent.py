from fastapi import APIRouter, HTTPException, Header, Depends
from api.schemas import AgentRequest, AgentResponse
from api.dependencies import build_agent
from app.infra.validators import InputValidator
import os

router = APIRouter(prefix="/agent", tags=["agent"])

# Global agent instance (lazy loaded)
_agent = None

def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent

# API Key verification
API_KEY = os.getenv("API_KEY", "supersecretkey")

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

@router.post("/run", response_model=AgentResponse)
async def run_agent(
    request: AgentRequest,
    _: None = Depends(verify_api_key),
    agent = Depends(get_agent)
):
    try:
        # Input validation
        try:
            validated_goal = InputValidator.validate_goal(request.goal)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # IMPORTANT: create_plan is now async
        plan = await agent.create_plan(validated_goal)

        execution_output = await agent.execute_plan(
            request.session_id,
            validated_goal,
            plan
        )

        return AgentResponse(
            result=execution_output["result"],
            request_id=execution_output["request_id"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
