"""
MOCK VECTOR DATABASE
"""
from typing import List, Dict

class MockVectorDB:
    def __init__(self):
        self.documents = {
            "sample.txt": {
                "id": "sample.txt",
                "text": "An embedding is a vector representation of text.",
                "metadata": {"source": "sample.txt"},
                "score": 0.9
            },
            "retrieval.txt": {
                "id": "retrieval.txt",
                "text": "A vector database stores embeddings and finds similar ones quickly.",
                "metadata": {"source": "retrieval.txt"},
                "score": 0.7
            }
        }
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        results = []
        for doc_id, doc in self.documents.items():
            results.append({
                'id': doc_id,
                'text': doc['text'],
                'metadata': doc['metadata'],
                'score': doc['score']
            })
        return results[:k]
