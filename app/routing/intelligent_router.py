"""
routing/intelligent_router.py
Enterprise execution router that delegates execution to ReliableExecutor,
applies confidence-based and failure-based fallbacks, and emits structured logs.
"""

import time
from typing import Optional, Dict, Any

from registry.tool_registry import ToolRegistry
from infra.reliable_executor import ReliableExecutor
from infra.logger import StructuredLogger


class IntelligentRouter:
    """
    Responsibilities:
    - Execute requested tool via ReliableExecutor
    - Inspect metadata (confidence, similarity, errors)
    - Apply intelligent fallback rules
    - Preserve structured execution metadata
    """

    def __init__(
        self,
        registry: ToolRegistry,
        reliable_executor: ReliableExecutor,
        logger: Optional[StructuredLogger] = None,
        similarity_threshold: float = 0.50,
    ):
        self.registry = registry
        self.reliable_executor = reliable_executor
        self.logger = logger
        self.similarity_threshold = similarity_threshold

    def execute(self, step: Dict[str, Any], request_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a single plan step.

        step: {"tool": "<tool_name>", "query": "<...>", ...}
        request_id: optional request trace id to include in logs.
        Returns a structured dict: {"status": "success"|"error", "data": ..., "metadata": {...}}
        """
        requested_tool_name = step.get("tool")
        if not requested_tool_name:
            return {
                "status": "error",
                "data": None,
                "metadata": {"error": "Missing 'tool' in step."}
            }

        # Execute primary tool via reliable executor
        try:
            tool = self.registry.get(requested_tool_name)
        except Exception as e:
            err = f"Tool not found: {requested_tool_name} ({e})"
            if self.logger:
                self.logger.log("router_tool_not_found", {"request_id": request_id, "tool": requested_tool_name, "error": err})
            return {"status": "error", "data": None, "metadata": {"error": err}}

        # Primary execution
        primary_response = self.reliable_executor.execute(tool, step)
        primary_response.setdefault("metadata", {})
        primary_response["metadata"]["requested_tool"] = requested_tool_name

        # Log primary execution event
        if self.logger:
            self.logger.log("router_primary_executed", {
                "request_id": request_id,
                "requested_tool": requested_tool_name,
                "metadata": primary_response.get("metadata", {}),
                "status": primary_response.get("status")
            })

        # If primary tool errored -> attempt web_search fallback (if not already web_search)
        if primary_response.get("status") == "error":
            if requested_tool_name != "web_search" and "web_search" in self.registry.list_tools():
                if self.logger:
                    self.logger.log("router_primary_failed_initiating_fallback", {
                        "request_id": request_id,
                        "from": requested_tool_name,
                        "error": primary_response.get("metadata", {}).get("error")
                    })

                fallback_tool = self.registry.get("web_search")
                fallback_response = self.reliable_executor.execute(fallback_tool, step)
                fallback_response.setdefault("metadata", {})
                fallback_response["metadata"]["fallback_from"] = requested_tool_name

                if self.logger:
                    self.logger.log("router_fallback_executed", {
                        "request_id": request_id,
                        "from": requested_tool_name,
                        "to": "web_search",
                        "metadata": fallback_response.get("metadata"),
                        "status": fallback_response.get("status")
                    })

                return fallback_response

            return primary_response

        # Confidence-based fallback (RAG similarity)
        if requested_tool_name == "rag_search":
            similarity = primary_response.get("metadata", {}).get("similarity")
            # Only fallback if similarity exists and is below threshold
            if similarity is not None and isinstance(similarity, (int, float)) and similarity < self.similarity_threshold:
                if self.logger:
                    self.logger.log("router_rag_low_confidence", {
                        "request_id": request_id,
                        "requested_tool": requested_tool_name,
                        "similarity": similarity,
                        "threshold": self.similarity_threshold
                    })

                if "web_search" in self.registry.list_tools():
                    fallback_tool = self.registry.get("web_search")
                    fallback_response = self.reliable_executor.execute(fallback_tool, step)
                    fallback_response.setdefault("metadata", {})
                    fallback_response["metadata"]["fallback_from"] = "rag_search"

                    if self.logger:
                        self.logger.log("router_rag_fallback_executed", {
                            "request_id": request_id,
                            "from": "rag_search",
                            "to": "web_search",
                            "similarity": similarity,
                            "metadata": fallback_response.get("metadata"),
                            "status": fallback_response.get("status")
                        })

                    return fallback_response

        # No fallback triggered; return primary response
        return primary_response
