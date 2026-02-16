import os
import sys
import time
import traceback

from services.planning_agent_service import PlanningAgentService

# Try to import both tools (web + rag). We'll use whichever is available / best.
try:
    from services.web_search_tool import WebSearchTool
except Exception:
    WebSearchTool = None

try:
    from services.rag_search_tool import RAGSearchTool
    from services.embedding_service import EmbeddingService
    from core.vector_store import VectorStore
    from services.retriever_service import RetrieverService
except Exception:
    RAGSearchTool = None
    EmbeddingService = None
    VectorStore = None
    RetrieverService = None


DATA_PATH = "data/sample.txt"
STORE_PATH = "data/vector_store.pkl"


def choose_tool_and_init():
    """
    Initialize available tools.
    Preference: initialize both if possible (hybrid).
    Use RAG first for private docs, then fallback to Web search if RAG returns no/weak results.
    """
    rag_tool = None
    web_tool = None
    embedding_service = None
    retriever = None
    vector_store = None

    # Initialize RAG tool if code is available
    if RAGSearchTool and EmbeddingService and VectorStore and RetrieverService:
        try:
            embedding_service = EmbeddingService()
            vector_store = VectorStore(DATA_PATH, STORE_PATH, embedding_service.model)
            retriever = RetrieverService(vector_store)
            rag_tool = RAGSearchTool(embedding_service, retriever)
            print("• RAG tool initialized (local vector store).")
        except Exception as e:
            print("⚠️ Failed to initialize RAG tool:", e)
            rag_tool = None

    # Initialize WebSearchTool if available and API key present
    if WebSearchTool is not None:
        # WebSearchTool raises ValueError if SERPAPI_KEY missing
        try:
            web_tool = WebSearchTool()
            print("• Web search tool initialized (SerpAPI).")
        except Exception as e:
            print("⚠️ Web search tool not available:", e)
            web_tool = None
    else:
        print("• Web search tool module not found.")

    return {
        "rag_tool": rag_tool,
        "web_tool": web_tool,
        "embedding_service": embedding_service,
        "retriever": retriever,
        "vector_store": vector_store,
    }


def best_search(toolset, query):
    """
    Hybrid search policy:
      1. Try RAG (private docs) if initialized.
         - If result is substantive (length threshold) -> use it.
      2. Else fallback to Web search if available.
      3. Return best result and a tag indicating source.
    """
    rag_tool = toolset.get("rag_tool")
    web_tool = toolset.get("web_tool")

    # Helper to evaluate result strength
    def is_strong_result(text):
        if not text:
            return False
        text = text.strip()
        if len(text) < 120:
            return False
        if "no relevant" in text.lower() or "no results" in text.lower():
            return False
        return True

    # 1) Try RAG first
    if rag_tool:
        try:
            rag_result = rag_tool.search(query)
            if is_strong_result(rag_result):
                return ("rag", rag_result)
            # If rag_result is weak, keep it as candidate but fallback to web
            rag_candidate = rag_result
        except Exception as e:
            print("⚠️ RAG search failed:", e)
            rag_candidate = None
    else:
        rag_candidate = None

    # 2) Fallback to web search
    if web_tool:
        try:
            web_result = web_tool.search(query)
            if is_strong_result(web_result):
                return ("web", web_result)
            web_candidate = web_result
        except Exception as e:
            print("⚠️ Web search failed:", e)
            web_candidate = None
    else:
        web_candidate = None

    # 3) Choose best available (prefer RAG candidate if substantive, else web candidate, else any)
    if rag_candidate:
        return ("rag", rag_candidate)
    if web_candidate:
        return ("web", web_candidate)

    return (None, "No relevant information found from any tool.")


def main():
    try:
        print("🔄 Initializing system (hybrid search agent)...")
        toolset = choose_tool_and_init()

        # If neither tool is available, abort
        if not toolset.get("rag_tool") and not toolset.get("web_tool"):
            print("❌ No search tools available. Please ensure rag_search_tool or web_search_tool is present and configured.")
            return

        # Initialize agent (planner + controller). Agent uses the 'tool' abstraction during deterministic execution.
        # We provide a minimal wrapper tool that will call best_search for each step.
        class HybridToolWrapper:
            def __init__(self, toolset):
                self.toolset = toolset

            def search(self, query):
                source, result = best_search(self.toolset, query)
                tag = source or "none"
                return f"[source={tag}]\n{result}"

        hybrid_tool = HybridToolWrapper(toolset)
        agent = PlanningAgentService(tool=hybrid_tool)

        print("✅ System ready.\n")

        goal = input("Enter complex goal: ").strip()
        if not goal:
            print("❌ Goal cannot be empty. Exiting.")
            return
        if len(goal) < 5:
            print("❌ Goal too short. Provide a meaningful objective.")
            return

        print("\n--- Generating Plan ---")
        plan = agent.create_plan(goal)
        if not plan or "Unsupported goal domain" in plan:
            print("❌ Planner could not generate valid plan.")
            return
        print(plan)

        print("\n--- Executing Plan ---")
        # Execute deterministically using HybridToolWrapper inside the PlanningAgentService
        result = agent.execute_plan(goal, plan)

        print("\n--- Final Result ---")
        print(result)

    except FileNotFoundError as e:
        print(f"❌ File error: {e}")
    except Exception:
        print("❌ Unexpected system error occurred.")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
