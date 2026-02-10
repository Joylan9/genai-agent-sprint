import os
import pickle
import hashlib


class VectorStore:
    def __init__(self, data_path, store_path, embedding_model):
        self.data_path = data_path
        self.store_path = store_path
        self.embedding_model = embedding_model
        self.documents = []
        self.embeddings = []

        self._initialize_store()

    def _get_file_hash(self):
        with open(self.data_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def _build_store(self):
        print("Building embeddings...")

        with open(self.data_path, "r", encoding="utf-8") as f:
            text = f.read()

        self.documents = [chunk.strip() for chunk in text.split("\n") if chunk.strip()]
        self.embeddings = self.embedding_model.encode(self.documents)
        file_hash = self._get_file_hash()

        with open(self.store_path, "wb") as f:
            pickle.dump((self.documents, self.embeddings, file_hash), f)

        print("Embeddings saved.")

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
            self.embeddings = embeds
            print("Embeddings are up to date.")

    def _initialize_store(self):
        if os.path.exists(self.store_path):
            self._load_store()
        else:
            self._build_store()
