import logging
import json
import uuid
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# ============================================================
# PROMETHEUS METRICS
# ============================================================

REQUEST_COUNTER = Counter(
    "agent_requests_total",
    "Total number of agent requests"
)

REQUEST_LATENCY = Histogram(
    "agent_request_latency_seconds",
    "End-to-end agent request latency",
    buckets=(0.1, 0.3, 0.5, 1, 2, 5, 10, 20)
)

TOOL_EXECUTION_COUNTER = Counter(
    "agent_tool_execution_total",
    "Total tool executions",
    ["tool_name", "status"]
)

TOOL_EXECUTION_LATENCY = Histogram(
    "agent_tool_latency_seconds",
    "Tool execution latency",
    ["tool_name"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1, 2, 5)
)

MEMORY_HIT_COUNTER = Counter(
    "agent_memory_hits_total",
    "Memory retrieval hits",
    ["memory_type"]
)

MEMORY_MISS_COUNTER = Counter(
    "agent_memory_miss_total",
    "Memory retrieval misses",
    ["memory_type"]
)

# ============================================================
# LLM OBSERVABILITY METRICS
# ============================================================

LLM_CALL_COUNTER = Counter(
    "llm_calls_total",
    "Total LLM inference calls",
    ["status"]
)

LLM_CALL_LATENCY = Histogram(
    "llm_call_latency_seconds",
    "LLM inference latency per call",
    buckets=(0.5, 1, 2, 5, 10, 15, 20, 30)
)

LLM_FAILURE_COUNTER = Counter(
    "llm_failures_total",
    "LLM transport/timeout failures",
    ["error_type"]
)

def metrics_response():
    return generate_latest(), CONTENT_TYPE_LATEST


# ============================================================
# STRUCTURED LOGGER
# ============================================================

class StructuredLogger:

    def __init__(self, name="agent"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(message)s"))
            self.logger.addHandler(handler)

    def log(self, event_type, payload):
        log_entry = {
            "event": event_type,
            "payload": payload
        }
        self.logger.info(json.dumps(log_entry))


def generate_request_id():
    return str(uuid.uuid4())
