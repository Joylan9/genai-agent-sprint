"""
Trace Evaluation Script
Enterprise AI Agent Engine
"""

import asyncio
from collections import Counter
from statistics import mean, median
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

    tool_latencies = []
    planner_latencies = []
    synthesis_latencies = []
    total_latencies = []

    memory_only = 0

    for trace in traces:
        steps = trace.get("steps", [])
        observations = trace.get("observations", [])
        latency_block = trace.get("latency", {})

        if not steps:
            empty_plans += 1
            memory_only += 1

        # ----------------------------
        # Tool-level stats
        # ----------------------------
        for obs in observations:
            tool = obs.get("tool")
            response = obs.get("response", {})
            metadata = response.get("metadata", {})

            if tool:
                tool_counter[tool] += 1

            if metadata.get("status") == "success":
                tool_success[tool] += 1
            else:
                tool_failure[tool] += 1

            if "total_execution_time" in metadata:
                tool_latencies.append(metadata["total_execution_time"])

        # ----------------------------
        # Request-level latency stats
        # ----------------------------
        if latency_block:
            if "planner" in latency_block:
                planner_latencies.append(latency_block["planner"])

            if "tool_total" in latency_block:
                tool_latencies.append(latency_block["tool_total"])

            if "synthesis" in latency_block:
                synthesis_latencies.append(latency_block["synthesis"])

            if "total" in latency_block:
                total_latencies.append(latency_block["total"])

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

    # ----------------------------
    # Latency Reporting Helper
    # ----------------------------
    def report_latency(name, values):
        if not values:
            return
        print(f"\n{name} (seconds):")
        print(f"  Average: {mean(values):.4f}")
        print(f"  Median : {median(values):.4f}")
        print(f"  Min    : {min(values):.4f}")
        print(f"  Max    : {max(values):.4f}")

        sorted_vals = sorted(values)
        index_95 = int(len(sorted_vals) * 0.95) - 1
        index_95 = max(0, min(index_95, len(sorted_vals) - 1))
        print(f"  p95    : {sorted_vals[index_95]:.4f}")

    report_latency("Planner Latency", planner_latencies)
    report_latency("Tool Latency (Aggregate)", tool_latencies)
    report_latency("Synthesis Latency", synthesis_latencies)
    report_latency("Total Request Latency", total_latencies)

    print("\n=============================================\n")


if __name__ == "__main__":
    asyncio.run(evaluate())
