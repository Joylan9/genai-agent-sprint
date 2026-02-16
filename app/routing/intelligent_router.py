class IntelligentRouter:
    def __init__(self, registry, similarity_threshold=0.50):
        self.registry = registry
        self.similarity_threshold = similarity_threshold

    def execute(self, step):
        """
        Execute tool with confidence-aware routing.
        """

        requested_tool_name = step["tool"]
        query = step["query"]

        tool = self.registry.get(requested_tool_name)

        response = tool.execute(step)

        # If RAG tool and similarity low → fallback
        if requested_tool_name == "rag_search":
            similarity = response.get("metadata", {}).get("similarity")

            if similarity is not None and similarity < self.similarity_threshold:
                print(f"[Router] Low RAG similarity ({similarity:.4f}) → Fallback to web_search")

                if "web_search" in self.registry.list_tools():
                    web_tool = self.registry.get("web_search")
                    return web_tool.execute(step)

        return response
