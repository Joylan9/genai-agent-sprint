from sentence_transformers import SentenceTransformer
import numpy as np

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Sample text
documents = [
    "Artificial Intelligence is the field of building machines.",
    "Machine Learning allows systems to learn from data.",
    "Embeddings represent text as numerical vectors."
]

# Generate embeddings
embeddings = model.encode(documents)

# Print shape
print("Embedding shape:", embeddings.shape)

# Compare similarity between first and third
similarity = np.dot(embeddings[0], embeddings[2])
print("Similarity between AI and Embeddings:", similarity)
