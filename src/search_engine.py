"""
FAISS-based vector search engine
"""
from pathlib import Path
from typing import List, Tuple
import numpy as np
import faiss
from .embedder import EmbeddingGenerator
from .cache_manager import CacheManager

class SearchEngine:
    def __init__(self):
        """Initialize search engine"""
        self.embedder = EmbeddingGenerator()
        self.cache = CacheManager()
        self.index = None
        self.doc_ids = []
        self.doc_texts = {}
        
    def build_index(self, docs_dir: str = "data/docs"):
        """Build FAISS index from documents"""
        docs_path = Path(docs_dir)
        doc_paths = sorted(docs_path.glob("*.txt"))
        
        if not doc_paths:
            raise ValueError(f"No documents found in {docs_dir}")
        
        print(f"Building index for {len(doc_paths)} documents...")
        
        # Get embeddings (from cache or generate)
        embeddings_dict = self.embedder.embed_documents(doc_paths)
        
        # Load document texts
        for doc_path in doc_paths:
            doc_id = doc_path.stem
            with open(doc_path, 'r', encoding='utf-8') as f:
                self.doc_texts[doc_id] = f.read()
        
        # Build FAISS index
        self.doc_ids = list(embeddings_dict.keys())
        embeddings_matrix = np.array([embeddings_dict[doc_id] for doc_id in self.doc_ids])
        
        dimension = embeddings_matrix.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
        self.index.add(embeddings_matrix.astype('float32'))
        
        print(f"✓ Index built with {self.index.ntotal} documents")
    
    def search(self, query: str, top_k: int = 5) -> List[dict]:
        """
        Search for similar documents
        Returns list of {doc_id, score, preview, explanation}
        """
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Embed query
        query_embedding = self.embedder.embed_text(query)
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Prepare results
        results = []
        query_words = set(query.lower().split())
        
        for score, idx in zip(scores[0], indices[0]):
            doc_id = self.doc_ids[idx]
            text = self.doc_texts[doc_id]
            
            # Generate explanation
            doc_words = set(text.lower().split())
            overlap = query_words & doc_words
            overlap_ratio = len(overlap) / len(query_words) if query_words else 0
            
            # Preview (first 150 chars)
            preview = text[:150] + "..." if len(text) > 150 else text
            
            results.append({
                "doc_id": doc_id,
                "score": float(score),
                "preview": preview,
                "explanation": {
                    "semantic_similarity": float(score),
                    "keyword_overlap": list(overlap)[:5],  # Top 5 overlapping words
                    "overlap_ratio": round(overlap_ratio, 2),
                    "doc_length": len(text.split())
                }
            })
        
        return results
    
    def get_document(self, doc_id: str) -> str:
        """Get full document text"""
        return self.doc_texts.get(doc_id, "")
