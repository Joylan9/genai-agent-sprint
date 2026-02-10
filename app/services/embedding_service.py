from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        print("Loading embedding model...")
        self.model = SentenceTransformer(model_name)

    def encode(self, texts):
        return self.model.encode(texts)
