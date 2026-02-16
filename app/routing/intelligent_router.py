class IntelligentRouter:
    """
    Enterprise execution router.

    Responsibilities:
    - Execute requested tool via ReliableExecutor
    - Inspect metadata (confidence, similarity, errors)
    - Apply intelligent fallback rules
    - Preserve structured execution metadata
    """

    def __init__(self, registry, reliable_executor, similarity_threshold=0.50):
        self.registry = registry
        self.reliable_executor = reliable_executor
        self.similarity_threshold = similarity_threshold

    def execute(self, step):

        requested_tool_name = step["tool"]

        # ------------------------------
        # Execute Primary Tool
        # ------------------------------
        tool = self.registry.get(requested_tool_name)
        response = self.reliable_executor.execute(tool, step)

        response.setdefault("metadata", {})
        response["metadata"]["requested_tool"] = requested_tool_name

        # ------------------------------
        # If primary tool failed → optional fallback
        # ------------------------------
        if response.get("status") == "error":
            if requested_tool_name != "web_search" and "web_search" in self.registry.list_tools():
                fallback_tool = self.registry.get("web_search")

                fallback_response = self.reliable_executor.execute(fallback_tool, step)
                fallback_response.setdefault("metadata", {})
                fallback_response["metadata"]["fallback_from"] = requested_tool_name

                return fallback_response

            return response

        # ------------------------------
        # RAG Confidence-Based Fallback
        # ------------------------------
        if requested_tool_name == "rag_search":

            similarity = response.get("metadata", {}).get("similarity")

            if similarity is not None and similarity < self.similarity_threshold:

                print(
                    f"[Router] RAG similarity {similarity:.4f} "
                    f"below threshold {self.similarity_threshold} → fallback to web"
                )

                if "web_search" in self.registry.list_tools():
                    fallback_tool = self.registry.get("web_search")

                    fallback_response = self.reliable_executor.execute(fallback_tool, step)
                    fallback_response.setdefault("metadata", {})
                    fallback_response["metadata"]["fallback_from"] = "rag_search"

                    return fallback_response

        return response
