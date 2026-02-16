class RAGSearchTool:
    def __init__(self, embedding_service, retriever):
        self.embedding_service = embedding_service
        self.retriever = retriever

    def search(self, query):
        query_embedding = self.embedding_service.encode([query])[0]
        contexts = self.retriever.retrieve(query_embedding)

        if not contexts:
            return "No relevant information found."

        return " ".join(contexts)
