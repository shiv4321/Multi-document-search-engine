"""
Embedding generation with caching
"""
import hashlib
from pathlib import Path
from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from .cache_manager import CacheManager

class EmbeddingGenerator:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize embedding model"""
        print(f"Loading model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.cache = CacheManager()
        
    def compute_hash(self, text: str) -> str:
        """Compute SHA256 hash of text"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for single text"""
        embedding = self.model.encode(text, convert_to_numpy=True)
        # Normalize for cosine similarity
        embedding = embedding / np.linalg.norm(embedding)
        return embedding
    
    def embed_documents(self, doc_paths: List[Path], force_recompute: bool = False) -> dict:
        """
        Embed all documents with caching
        Returns: {doc_id: embedding}
        """
        results = {}
        to_embed = []
        
        print(f"Processing {len(doc_paths)} documents...")
        
        for doc_path in doc_paths:
            doc_id = doc_path.stem
            
            # Read document
            with open(doc_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            text_hash = self.compute_hash(text)
            
            # Check cache
            if not force_recompute:
                cached = self.cache.get(doc_id, text_hash)
                if cached is not None:
                    results[doc_id] = cached
                    continue
            
            # Need to embed
            to_embed.append((doc_id, text, text_hash))
        
        # Batch embed
        if to_embed:
            print(f"Embedding {len(to_embed)} new/changed documents...")
            texts = [item[1] for item in to_embed]
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
            
            # Normalize
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            
            # Cache and store
            for (doc_id, _, text_hash), embedding in zip(to_embed, embeddings):
                self.cache.set(doc_id, embedding, text_hash)
                results[doc_id] = embedding
        
        print(f"✓ Total embeddings: {len(results)}")
        return results

def main():
    """CLI tool to generate embeddings"""
    docs_dir = Path("data/docs")
    
    if not docs_dir.exists():
        print("Error: data/docs/ not found. Run setup.py first!")
        return
    
    doc_paths = list(docs_dir.glob("*.txt"))
    
    if not doc_paths:
        print("No documents found!")
        return
    
    embedder = EmbeddingGenerator()
    embeddings = embedder.embed_documents(doc_paths)
    
    print(f"\\n✓ Generated {len(embeddings)} embeddings")
    print("Cache stored in: data/cache/embeddings.db")

if __name__ == "__main__":
    main()