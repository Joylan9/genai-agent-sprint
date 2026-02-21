from app.services.agent_service import AgentService
from app.services.tools import SimpleSearchTool


def main():
    tool = SimpleSearchTool()
    agent = AgentService(tool=tool)

    goal = input("Enter goal: ")
    result = agent.run(goal)

    print("\nFinal Result:\n", result)


if __name__ == "__main__":
    main()
