"""
Test: Real retrieval with real embeddings
"""
from src.indexer import Indexer
from src.embeddings import LocalEmbeddings
from src.retriever import InstrumentedRetriever

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

print("=" * 60)
print("WEEK 2: Real Embeddings Retrieval Test")
print("=" * 60)

# Index documents
print("\nIndexing documents...")
indexer = Indexer()
indexer.index_documents(documents)

# Create retriever with embeddings
embeddings = LocalEmbeddings()
retriever = InstrumentedRetriever(indexer.vectordb, embeddings=embeddings, top_k=3)

# Test query
query = "What is an embedding?"
relevant_docs = ['sample.txt']

print(f"\nQuery: '{query}'")
print(f"Expected: {relevant_docs}")

documents_retrieved, metrics = retriever.retrieve(query, ground_truth_doc_ids=relevant_docs)

print(f"\nRetrieved:")
for i, doc in enumerate(documents_retrieved, 1):
    print(f"  {i}. {doc['id']} (score: {doc['score']:.2f})")

print(f"\nMetrics:")
print(f"  Precision: {metrics.precision_at_k:.2f}")
print(f"  Recall: {metrics.recall_at_k:.2f}")
print(f"  MRR: {metrics.mrr:.2f}")

print("\n✨ Week 2 test complete!")
