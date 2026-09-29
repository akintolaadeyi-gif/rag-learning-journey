import json
from src.retriever import InstrumentedRetriever
from src.mock_vectordb import MockVectorDB

with open('data/eval_dataset.json') as f:
    eval_data = json.load(f)

vdb = MockVectorDB()
retriever = InstrumentedRetriever(vdb, top_k=3)

question = eval_data[0]['question']
relevant_docs = eval_data[0]['relevant_doc_ids']

print(f"\n📋 Question: {question}")
print(f"📚 Expected: {relevant_docs}")

documents, metrics = retriever.retrieve(question, ground_truth_doc_ids=relevant_docs)

print(f"\n✅ Retrieved:")
for i, doc in enumerate(documents, 1):
    print(f"   {i}. {doc['id']} (score: {doc['score']:.2f})")

print(f"\n📊 Metrics:")
print(f"   Precision: {metrics.precision_at_k:.2f}")
print(f"   Recall: {metrics.recall_at_k:.2f}")
print(f"   MRR: {metrics.mrr:.2f}")

print("\n✨ Success!")
