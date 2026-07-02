from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        print("Loading embedding model...")
        self.model = SentenceTransformer(model_name)

    def encode(self, texts):
        return self.model.encode(texts)

    # ✅ Fixed for Memory Layer compatibility (safe conversion)
    def embed_text(self, text: str):
        embedding = self.model.encode(text)

        # If numpy array → convert to list
        if hasattr(embedding, "tolist"):
            return embedding.tolist()

        # If already list → return directly
        return embedding
