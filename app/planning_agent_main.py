from services.planning_agent_service import PlanningAgentService
from services.tools import SimpleSearchTool


def main():
    tool = SimpleSearchTool()
    agent = PlanningAgentService(tool=tool)

    goal = input("Enter complex goal: ")

    print("\n--- Generating Plan ---")
    plan = agent.create_plan(goal)
    print(plan)

    print("\n--- Executing Plan ---")
    result = agent.execute_plan(goal, plan)

    print("\nFinal Result:\n", result)


if __name__ == "__main__":
    main()
