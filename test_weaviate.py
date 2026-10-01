"""
Test: Index documents into Weaviate
"""
from src.indexer import Indexer
from src.embeddings import LocalEmbeddings

# Sample documents
documents = [
    {
        'id': 'sample.txt',
        'text': 'An embedding is a vector representation of text. It converts words into numbers that capture meaning.'
    },
    {
        'id': 'retrieval.txt',
        'text': 'A vector database stores embeddings and finds similar ones quickly. Unlike traditional databases that search by keywords, vector databases search by meaning.'
    },
    {
        'id': 'hallucination.txt',
        'text': 'Hallucination occurs when an LLM generates text that is not supported by the provided context.'
    }
]

print("=" * 50)
print("WEEK 2: Weaviate + Real Embeddings")
print("=" * 50)

# Index documents
print("\nIndexing documents...")
indexer = Indexer()
indexer.index_documents(documents)

# Test embedding
print("\nTesting embeddings...")
embeddings = LocalEmbeddings()
query = "What is an embedding?"
query_emb = embeddings.embed_text(query)
print(f"Query: '{query}'")
print(f"Embedding size: {len(query_emb)} dimensions")
print(f"First 5 values: {query_emb[:5]}")

print("\nSuccess!")
