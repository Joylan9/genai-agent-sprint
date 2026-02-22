import numpy as np
from app.services.retriever_service import RetrieverService

class MockVectorStore:
    def __init__(self, documents, embeddings):
        self.documents = documents
        self.document_embeddings = np.array(embeddings, dtype=np.float32)

def debug_retriever():
    docs = [
        "Reliability is about circuit breakers and timeouts.",
        "Security involves redaction and guardrails.",
        "Architecture uses a modular design."
    ]
    embeds = [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0]
    ]
    store = MockVectorStore(docs, embeds)
    retriever = RetrieverService(store)
    
    query_embed = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
    print("Testing retrieve...")
    try:
        results = retriever.retrieve(query_embed, top_k=1)
        print(f"Results: {results}")
    except Exception as e:
        print(f"Error during retrieve: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_retriever()
