"""
api/app.py
FastAPI entrypoint for the Enterprise AI Agent Engine.
"""

import os
from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.responses import JSONResponse
from api.schemas import AgentRequest, AgentResponse
from api.dependencies import build_agent
from app.infra.validators import InputValidator
from app.memory.database import MongoDB  # ✅ Added

app = FastAPI(
    title="Enterprise AI Agent Engine",
    version="1.0.0",
    description="Production-ready AI agent with routing, reliability, and hybrid search."
)

# ============================================================
# MONGODB STARTUP INITIALIZATION
# ============================================================
@app.on_event("startup")
async def startup_event():
    MongoDB.connect()
    await MongoDB.initialize_indexes()
    print("✅ MongoDB connected and indexes ensured.")


# Build agent once at startup
agent = build_agent()

# Load API key from environment
API_KEY = os.getenv("API_KEY", "supersecretkey")

# Maximum allowed request size (currently 1KB for testing)
MAX_REQUEST_SIZE = 1000
# MAX_REQUEST_SIZE = 1 * 1024 * 1024  # 1MB for production


# ============================================================
# REQUEST SIZE MIDDLEWARE
# ============================================================
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    body = await request.body()
    body_size = len(body)

    print(f"[DEBUG] Incoming request size: {body_size} bytes")

    if body_size > MAX_REQUEST_SIZE:
        print("[DEBUG] Request blocked due to size limit.")
        return JSONResponse(
            status_code=413,
            content={"detail": "Request size exceeds allowed limit."},
        )

    async def receive():
        return {"type": "http.request", "body": body}

    request._receive = receive

    return await call_next(request)


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
async def run_agent(   # ✅ changed to async
    request: AgentRequest,
    _: None = Depends(verify_api_key),
):
    try:
        # Input validation
        try:
            validated_goal = InputValidator.validate_goal(request.goal)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        plan = agent.create_plan(validated_goal)

        execution_output = await agent.execute_plan(  # ✅ added await
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
