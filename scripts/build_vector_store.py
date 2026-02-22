import os
import pickle
import hashlib
import glob
from sentence_transformers import SentenceTransformer

# Paths
DOCS_DIR = "data/docs"
STORE_PATH = "data/vector_store.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"

def main():
    print(f"Building vector store from {DOCS_DIR}...")
    
    # Initialize model
    model = SentenceTransformer(MODEL_NAME)
    
    documents = []
    
    # Recursive glob to find all markdown and text files
    files = glob.glob(os.path.join(DOCS_DIR, "**/*.md"), recursive=True)
    files.extend(glob.glob(os.path.join(DOCS_DIR, "**/*.txt"), recursive=True))
    
    if not files:
        print(f"No documents found in {DOCS_DIR}!")
        return

    for file_path in files:
        print(f"Processing {file_path}...")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
            # Simple chunking by paragraph/section
            chunks = [c.strip() for c in content.split("\n\n") if c.strip()]
            documents.extend(chunks)
            
    if not documents:
        print("No valid chunks found!")
        return
        
    print(f"Total chunks: {len(documents)}")
    
    # Generate embeddings
    embeddings = model.encode(documents, show_progress_bar=True)
    
    # Simple hash of all file contents to detect changes
    combined_hash = hashlib.md5("".join(files).encode()).hexdigest()
    
    # Save to pickle
    with open(STORE_PATH, "wb") as f:
        pickle.dump((documents, embeddings, combined_hash), f)
        
    print(f"Vector store saved to {STORE_PATH}")

if __name__ == "__main__":
    main()
