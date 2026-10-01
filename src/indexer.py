"""
INDEXER
Loads documents with real embeddings
"""
from src.embeddings import LocalEmbeddings
from src.in_memory_vectordb import InMemoryVectorDB
from typing import List, Dict

class Indexer:
    def __init__(self):
        self.embeddings = LocalEmbeddings()
        self.vectordb = InMemoryVectorDB()
    
    def index_documents(self, documents: List[Dict]):
        """Load documents with embeddings"""
        print(f"\nIndexing {len(documents)} documents...")
        
        for i, doc in enumerate(documents, 1):
            doc_id = doc['id']
            text = doc['text']
            
            # Generate embedding
            embedding = self.embeddings.embed_text(text)
            
            # Add to database
            self.vectordb.add_document(doc_id, text, embedding)
            
            print(f"  {i}. {doc_id}")
        
        print(f"\nIndexing complete!")
