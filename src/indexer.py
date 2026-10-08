"""
INDEXER
Loads documents with real embeddings into any vector store
"""
from src.embeddings import LocalEmbeddings
from src.in_memory_vectordb import InMemoryVectorDB
from typing import List, Dict

class Indexer:
    def __init__(self, vectordb=None, embeddings=None):
        # Defaults keep the original behaviour: local model, in-memory store
        self.embeddings = embeddings or LocalEmbeddings()
        self.vectordb = vectordb or InMemoryVectorDB()
    
    def index_documents(self, documents: List[Dict], verbose: bool = True):
        """Load documents with embeddings"""
        if verbose:
            print(f"\nIndexing {len(documents)} documents into {type(self.vectordb).__name__}...")
        
        # Embed all texts in one batch: much faster than one at a time
        vectors = self.embeddings.embed_texts([doc['text'] for doc in documents])
        
        for i, (doc, embedding) in enumerate(zip(documents, vectors), 1):
            self.vectordb.add_document(doc['id'], doc['text'], embedding)
            if verbose:
                print(f"  {i}. {doc['id']}")
        
        if verbose:
            print("Indexing complete!")
