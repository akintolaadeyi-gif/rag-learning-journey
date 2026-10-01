"""
EMBEDDINGS MODULE
Generate embeddings locally using sentence-transformers (FREE)
"""
from sentence_transformers import SentenceTransformer
from typing import List

class LocalEmbeddings:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embeddings model
        
        all-MiniLM-L6-v2: Small, fast, free (384 dimensions)
        This runs 100% locally on your computer
        """
        print(f"Loading embeddings model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("Model loaded")
    
    def embed_text(self, text: str) -> List[float]:
        """Convert text to embedding (vector of numbers)"""
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Convert multiple texts to embeddings"""
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
