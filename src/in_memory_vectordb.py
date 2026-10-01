"""
IN-MEMORY VECTOR DATABASE
Store embeddings in memory (no network needed)
"""
from typing import List, Dict
import numpy as np

class InMemoryVectorDB:
    def __init__(self):
        self.documents = {}
        self.embeddings = {}
    
    def add_document(self, doc_id: str, text: str, embedding: List[float]):
        """Store document with embedding"""
        self.documents[doc_id] = text
        self.embeddings[doc_id] = np.array(embedding)
    
    def search(self, query_embedding: List[float], k: int = 5) -> List[Dict]:
        """Find similar documents using cosine similarity"""
        query_vec = np.array(query_embedding)
        
        results = []
        for doc_id, doc_embedding in self.embeddings.items():
            # Cosine similarity
            similarity = np.dot(query_vec, doc_embedding) / (
                np.linalg.norm(query_vec) * np.linalg.norm(doc_embedding) + 1e-8
            )
            
            results.append({
                'id': doc_id,
                'text': self.documents[doc_id],
                'metadata': {'source': doc_id},
                'score': float(similarity)
            })
        
        # Sort by score (highest first)
        results = sorted(results, key=lambda x: x['score'], reverse=True)
        return results[:k]
