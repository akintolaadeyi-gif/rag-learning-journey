"""
MOCK VECTOR DATABASE

Loads the real corpus but ignores the query entirely and returns documents
in file order with made-up scores. This is deliberately a "no intelligence"
baseline: any real retriever (BM25 on Day 3, embeddings on Day 4) has to
beat these numbers to prove it is doing anything.
"""
import json
from pathlib import Path
from typing import Dict, List

DEFAULT_CORPUS = Path(__file__).resolve().parent.parent / "data" / "corpus.json"


class MockVectorDB:
    def __init__(self, corpus_path: Path = DEFAULT_CORPUS):
        with open(corpus_path) as f:
            self.documents = json.load(f)

    def search(self, query: str, k: int = 5) -> List[Dict]:
        results = []
        for i, doc in enumerate(self.documents[:k]):
            results.append({
                "id": doc["id"],
                "text": doc["text"],
                "metadata": {"source": "corpus.json"},
                "score": round(1.0 - i * 0.1, 2),  # fake, descending
            })
        return results
