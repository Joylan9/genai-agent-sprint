from fastapi import FastAPI, HTTPException
from api.schemas import AgentRequest, AgentResponse
from api.dependencies import build_agent

app = FastAPI(title="Enterprise AI Agent Engine")

agent = build_agent()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/agent/run", response_model=AgentResponse)
def run_agent(request: AgentRequest):
    try:
        plan = agent.create_plan(request.goal)
        result = agent.execute_plan(request.goal, plan)

        return AgentResponse(result=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
