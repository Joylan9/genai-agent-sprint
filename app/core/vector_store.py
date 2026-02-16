import os
import pickle
import hashlib
import numpy as np


class VectorStore:
    def __init__(self, data_path, store_path, embedding_model):
        self.data_path = data_path
        self.store_path = store_path
        self.embedding_model = embedding_model

        # PUBLIC CONTRACT (used by RAGSearchTool)
        self.documents = []  # List[str]
        self.document_embeddings = None  # np.ndarray (N, dim)

        self._initialize_store()

    # ------------------------------------------------
    # File hash (used to detect content change)
    # ------------------------------------------------
    def _get_file_hash(self):
        with open(self.data_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    # ------------------------------------------------
    # Build embeddings from scratch
    # ------------------------------------------------
    def _build_store(self):
        print("Building embeddings...")

        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"{self.data_path} not found.")

        with open(self.data_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Simple chunking (can upgrade later)
        self.documents = [
            chunk.strip()
            for chunk in text.split("\n")
            if chunk.strip()
        ]

        if not self.documents:
            raise ValueError("No valid documents found in data file.")

        embeddings = self.embedding_model.encode(self.documents)

        # Convert to numpy array for similarity computation
        self.document_embeddings = np.asarray(embeddings, dtype=np.float32)

        file_hash = self._get_file_hash()

        with open(self.store_path, "wb") as f:
            pickle.dump(
                (self.documents, self.document_embeddings, file_hash),
                f
            )

        print("Embeddings saved.")

    # ------------------------------------------------
    # Load embeddings from disk
    # ------------------------------------------------
    def _load_store(self):
        print("Loading embeddings from disk...")

        with open(self.store_path, "rb") as f:
            docs, embeds, saved_hash = pickle.load(f)

        current_hash = self._get_file_hash()

        if current_hash != saved_hash:
            print("Data changed. Rebuilding index...")
            self._build_store()
        else:
            self.documents = docs
            self.document_embeddings = np.asarray(embeds, dtype=np.float32)
            print("Embeddings are up to date.")

    # ------------------------------------------------
    # Initialize store (load or build)
    # ------------------------------------------------
    def _initialize_store(self):
        if os.path.exists(self.store_path):
            self._load_store()
        else:
            self._build_store()
