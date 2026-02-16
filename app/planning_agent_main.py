import sys
import traceback

from services.planning_agent_service import PlanningAgentService

# Optional tool imports
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


# ============================================================
# TOOL INITIALIZATION
# ============================================================

def choose_tool_and_init():
    rag_tool = None
    web_tool = None

    # Initialize RAG
    if RAGSearchTool and EmbeddingService and VectorStore and RetrieverService:
        try:
            embedding_service = EmbeddingService()
            vector_store = VectorStore(DATA_PATH, STORE_PATH, embedding_service.model)
            retriever = RetrieverService(vector_store)
            rag_tool = RAGSearchTool(embedding_service, retriever)
            print("• RAG tool initialized (local vector store).")
        except Exception as e:
            print("⚠️ Failed to initialize RAG tool:", e)

    # Initialize Web Search
    if WebSearchTool is not None:
        try:
            web_tool = WebSearchTool()
            print("• Web search tool initialized (SerpAPI).")
        except Exception as e:
            print("⚠️ Web search tool not available:", e)
    else:
        print("• Web search tool module not found.")

    return {
        "rag_tool": rag_tool,
        "web_tool": web_tool,
    }


# ============================================================
# HYBRID SEARCH WRAPPER (ENTERPRISE VERSION)
# ============================================================

class HybridToolWrapper:
    """
    Enterprise Hybrid Search Routing

    Strategy:
      1. Query RAG with top_k results.
      2. Compute max similarity score.
      3. If score >= threshold → use RAG.
      4. Otherwise → fallback to Web search.
    """

    def __init__(self, toolset, similarity_threshold=0.50, top_k=3):
        self.toolset = toolset
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k

    def search(self, query):
        rag_tool = self.toolset.get("rag_tool")
        web_tool = self.toolset.get("web_tool")

        # ------------------------------
        # 1️⃣ Try RAG First
        # ------------------------------
        if rag_tool:
            try:
                docs, scores = rag_tool.search_with_score(query, top_k=self.top_k)

                max_score = max(scores)
                print(f"[RAG similarity score: {max_score:.4f}]")

                if max_score >= self.similarity_threshold:
                    print("→ Using RAG (high confidence)")

                    combined = "\n\n".join(
                        f"[score={s:.4f}]\n{d}"
                        for d, s in zip(docs, scores)
                    )

                    return f"[source=rag | confidence={max_score:.4f}]\n{combined}"

                print("→ RAG confidence LOW → fallback to Web.")

            except Exception as e:
                print("⚠️ RAG failure:", e)

        # ------------------------------
        # 2️⃣ Fallback to Web
        # ------------------------------
        if web_tool:
            try:
                web_result = web_tool.search(query)
                return "[source=web]\n" + web_result
            except Exception as e:
                return f"Web search failed: {e}"

        return "No search tools available."


# ============================================================
# MAIN ENTRY
# ============================================================

def main():
    try:
        print("🔄 Initializing system (hybrid search agent)...")

        toolset = choose_tool_and_init()

        if not toolset.get("rag_tool") and not toolset.get("web_tool"):
            print("❌ No search tools available.")
            return

        hybrid_tool = HybridToolWrapper(toolset)
        agent = PlanningAgentService(tool=hybrid_tool)

        print("✅ System ready.\n")

        goal = input("Enter complex goal: ").strip()

        if not goal:
            print("❌ Goal cannot be empty.")
            return

        if len(goal) < 5:
            print("❌ Goal too short.")
            return

        print("\n--- Generating Plan ---")
        plan = agent.create_plan(goal)
        print(plan)

        print("\n--- Executing Plan ---")
        result = agent.execute_plan(goal, plan)

        print("\n--- Final Result ---")
        print(result)

    except Exception:
        print("❌ Unexpected system error occurred.")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
