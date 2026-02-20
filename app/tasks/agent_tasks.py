from app.infra.celery_app import celery_app
from app.services.planning_agent_service import PlanningAgentService

@celery_app.task(name="agent.run_goal")
def run_agent_goal(session_id: str, goal: str):
    service = PlanningAgentService()
    result = service.run(goal=goal, session_id=session_id)
    return result