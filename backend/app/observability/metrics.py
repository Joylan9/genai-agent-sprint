"""
Prometheus metrics registry.
"""

from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter(
    "agent_requests_total",
    "Total requests received"
)

CACHE_HITS = Counter(
    "agent_cache_hits_total",
    "Total cache hits"
)

ACTIVE_REQUESTS = Gauge(
    "agent_active_requests",
    "Currently active requests"
)

PLANNER_LATENCY = Histogram(
    "agent_planner_latency_seconds",
    "Planner latency"
)

TOOL_LATENCY = Histogram(
    "agent_tool_latency_seconds",
    "Tool execution latency"
)

SYNTHESIS_LATENCY = Histogram(
    "agent_synthesis_latency_seconds",
    "Synthesis latency"
)
