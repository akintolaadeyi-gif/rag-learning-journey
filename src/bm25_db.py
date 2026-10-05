"""
BM25 KEYWORD SEARCH
Written from scratch so every part of the score is visible.

For each query word that appears in a document, BM25 adds:

    idf(word) * tf * (k1 + 1) / (tf + k1 * (1 - b + b * doc_len / avg_doc_len))

idf  rare words count more than common ones ("bm25" beats "the")
tf   how often the word appears in this document, with diminishing returns (k1)
b    long documents get penalised a little, so they do not win just by being long
"""
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List

DEFAULT_CORPUS = Path(__file__).resolve().parent.parent / "data" / "corpus.json"

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does", "for",
    "from", "how", "i", "if", "in", "is", "it", "its", "me", "my", "of", "on",
    "or", "so", "that", "the", "their", "them", "they", "this", "to", "what",
    "when", "where", "which", "who", "why", "with", "you",
}


def tokenize(text: str) -> List[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in STOPWORDS]


class BM25DB:
    def __init__(self, corpus_path: Path = DEFAULT_CORPUS, k1: float = 1.5, b: float = 0.75):
        with open(corpus_path) as f:
            self.documents = json.load(f)
        self.k1 = k1
        self.b = b

        self.doc_tokens = [tokenize(d["text"]) for d in self.documents]
        self.doc_freqs = [Counter(tokens) for tokens in self.doc_tokens]
        self.avg_len = sum(len(t) for t in self.doc_tokens) / len(self.doc_tokens)

        # How many documents contain each word
        df = Counter(word for tokens in self.doc_tokens for word in set(tokens))
        n = len(self.documents)
        self.idf = {w: math.log(1 + (n - c + 0.5) / (c + 0.5)) for w, c in df.items()}

    def score(self, query: str, index: int) -> float:
        freqs = self.doc_freqs[index]
        length_norm = 1 - self.b + self.b * len(self.doc_tokens[index]) / self.avg_len
        total = 0.0
        for word in tokenize(query):
            tf = freqs.get(word, 0)
            if tf:
                total += self.idf[word] * tf * (self.k1 + 1) / (tf + self.k1 * length_norm)
        return total

    def search(self, query: str, k: int = 5) -> List[Dict]:
        scored = [(self.score(query, i), doc) for i, doc in enumerate(self.documents)]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [
            {"id": doc["id"], "text": doc["text"], "metadata": {"source": "corpus.json"}, "score": round(s, 3)}
            for s, doc in scored[:k]
        ]
