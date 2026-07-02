import pytest
import numpy as np
from app.services.retriever_service import RetrieverService

class MiniMockVectorStore:
    def __init__(self, documents, embeddings):
        self.documents = documents
        self.document_embeddings = np.array(embeddings, dtype=np.float32)

@pytest.fixture
def mini_retriever():
    docs = ["Doc A", "Doc B"]
    embeds = [[1, 0, 0], [0, 1, 0]]
    store = MiniMockVectorStore(docs, embeds)
    return RetrieverService(store)

def test_retriever_simple(mini_retriever):
    query = np.array([1, 0, 0], dtype=np.float32)
    results = mini_retriever.retrieve(query, top_k=1)
    assert len(results) == 1
    assert results[0] == "Doc A"
