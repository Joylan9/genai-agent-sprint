import hashlib
import re

import numpy as np
from sentence_transformers import SentenceTransformer


class HashEmbeddingModel:
    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions

    def encode(self, texts):
        single_input = isinstance(texts, str)
        values = [texts] if single_input else list(texts)
        embeddings = [self._embed_text(value) for value in values]
        encoded = np.asarray(embeddings, dtype=np.float32)
        return encoded[0] if single_input else encoded

    def _embed_text(self, text: str):
        vector = np.zeros(self.dimensions, dtype=np.float32)
        tokens = re.findall(r"[a-z0-9]+", str(text).lower())
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector


class EmbeddingService:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        print("Loading embedding model...")
        try:
            self.model = SentenceTransformer(model_name, local_files_only=True)
        except Exception as exc:
            print(f"Embedding model unavailable locally; using hash embeddings. Reason: {exc}")
            self.model = HashEmbeddingModel()

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
