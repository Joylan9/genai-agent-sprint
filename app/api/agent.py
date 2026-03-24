from fastapi import APIRouter, HTTPException, Depends
from api.schemas import AgentRequest, AgentResponse
from api.dependencies import build_agent
from app.infra.validators import InputValidator
from app.api.auth import require_role

router = APIRouter(prefix="/agent", tags=["agent"])

# Global agent instance (lazy loaded)
_agent = None

def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent

@router.post("/run", response_model=AgentResponse)
async def run_agent(
    request: AgentRequest,
    _: dict = Depends(require_role("developer", "admin")),
    agent = Depends(get_agent)
):
    try:
        # Input validation
        try:
            validated_goal = InputValidator.validate_goal(request.goal)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        execution_output = await agent.run_goal(
            request.session_id,
            validated_goal,
            agent_id=request.agent_id,
        )

        return AgentResponse(
            result=execution_output["result"],
            request_id=execution_output["request_id"],
            status=execution_output.get("status"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
