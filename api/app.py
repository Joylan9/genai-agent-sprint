"""
api/app.py
FastAPI entrypoint for the Enterprise AI Agent Engine.
"""

import os
from fastapi import FastAPI, HTTPException, Header, Depends
from api.schemas import AgentRequest, AgentResponse
from api.dependencies import build_agent

app = FastAPI(
    title="Enterprise AI Agent Engine",
    version="1.0.0",
    description="Production-ready AI agent with routing, reliability, and hybrid search."
)

# Build agent once at startup
agent = build_agent()

# Load API key from environment
API_KEY = os.getenv("API_KEY", "supersecretkey")


# ============================================================
# API KEY DEPENDENCY
# ============================================================
def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/agent/run", response_model=AgentResponse)
def run_agent(
    request: AgentRequest,
    _: None = Depends(verify_api_key),  # 🔐 Enforce API key
):
    try:
        plan = agent.create_plan(request.goal)
        result = agent.execute_plan(request.goal, plan)

        return AgentResponse(result=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
