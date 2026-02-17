"""
Trace Evaluation Script
Enterprise AI Agent Engine
"""

import asyncio
from collections import Counter
from statistics import mean
from motor.motor_asyncio import AsyncIOMotorClient
import os


MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB", "agent_memory")


async def evaluate():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]

    traces = []
    async for doc in db.traces.find():
        traces.append(doc)

    if not traces:
        print("No traces found.")
        return

    total_requests = len(traces)
    empty_plans = 0
    tool_counter = Counter()
    tool_success = Counter()
    tool_failure = Counter()
    latencies = []
    memory_only = 0

    for trace in traces:
        steps = trace.get("steps", [])
        observations = trace.get("observations", [])

        if not steps:
            empty_plans += 1
            memory_only += 1

        for obs in observations:
            tool = obs.get("tool")
            response = obs.get("response", {})
            metadata = response.get("metadata", {})

            tool_counter[tool] += 1

            if metadata.get("status") == "success":
                tool_success[tool] += 1
            else:
                tool_failure[tool] += 1

            if "total_execution_time" in metadata:
                latencies.append(metadata["total_execution_time"])

    print("\n========== TRACE EVALUATION REPORT ==========")
    print(f"Total Requests: {total_requests}")
    print(f"Empty Plan Rate: {(empty_plans / total_requests) * 100:.2f}%")
    print(f"Memory-only Answers: {memory_only}")
    print()

    print("Tool Usage:")
    for tool, count in tool_counter.items():
        print(f"  {tool}: {count} calls")

    print("\nTool Success Rates:")
    for tool in tool_counter:
        total = tool_success[tool] + tool_failure[tool]
        if total > 0:
            success_rate = (tool_success[tool] / total) * 100
            print(f"  {tool}: {success_rate:.2f}% success")

    if latencies:
        print(f"\nAverage Tool Latency: {mean(latencies):.4f} seconds")

    print("\n=============================================\n")


if __name__ == "__main__":
    asyncio.run(evaluate())
