"""
SQLite-based embedding cache
"""
import sqlite3
from pathlib import Path
from typing import Optional
import numpy as np
from datetime import datetime

class CacheManager:
    def __init__(self, cache_path: str = "data/cache/embeddings.db"):
        """Initialize cache database"""
        self.cache_path = Path(cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Create cache table if not exists"""
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                doc_id TEXT PRIMARY KEY,
                embedding BLOB NOT NULL,
                hash TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get(self, doc_id: str, current_hash: str) -> Optional[np.ndarray]:
        """
        Get cached embedding if hash matches
        Returns None if not found or hash mismatch
        """
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT embedding, hash FROM embeddings WHERE doc_id = ?",
            (doc_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        stored_embedding, stored_hash = row
        
        # Check if hash matches
        if stored_hash != current_hash:
            return None
        
        # Deserialize
        embedding = np.frombuffer(stored_embedding, dtype=np.float32)
        return embedding
    
    def set(self, doc_id: str, embedding: np.ndarray, text_hash: str):
        """Store embedding in cache"""
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        
        # Serialize
        embedding_blob = embedding.astype(np.float32).tobytes()
        timestamp = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO embeddings (doc_id, embedding, hash, updated_at)
            VALUES (?, ?, ?, ?)
        """, (doc_id, embedding_blob, text_hash, timestamp))
        
        conn.commit()
        conn.close()
    
    def get_all(self) -> dict:
        """Get all cached embeddings"""
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT doc_id, embedding FROM embeddings")
        rows = cursor.fetchall()
        conn.close()
        
        results = {}
        for doc_id, embedding_blob in rows:
            embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            results[doc_id] = embedding
        
        return results
    
    def clear(self):
        """Clear all cache"""
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM embeddings")
        conn.commit()
        conn.close()
