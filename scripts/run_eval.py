"""
Run the eval set through each retriever and compare them side by side.

Usage (from the project root):
    python -m scripts.run_eval
    python -m scripts.run_eval --verbose   # per-question results
"""
import json
import sys
from pathlib import Path
from statistics import mean

from src.mock_vectordb import MockVectorDB
from src.retriever import InstrumentedRetriever

ROOT = Path(__file__).resolve().parent.parent
TOP_K = 3


def load(name):
    with open(ROOT / "data" / name) as f:
        return json.load(f)


def evaluate(name, retriever, eval_data, verbose):
    for item in eval_data:
        docs, m = retriever.retrieve(item["question"], ground_truth_doc_ids=item["relevant_doc_ids"])
        if verbose:
            print(f"[{name}] {item['question']}")
            print(f"    got {[d['id'] for d in docs]}  expected {item['relevant_doc_ids']}")
            print(f"    P={m.precision_at_k:.2f}  R={m.recall_at_k:.2f}  MRR={m.mrr:.2f}")
    log = retriever.metrics_log
    return {
        "precision": mean(m.precision_at_k for m in log),
        "recall": mean(m.recall_at_k for m in log),
        "mrr": mean(m.mrr for m in log),
        "latency_ms": mean(m.retrieval_time_ms for m in log),
    }


def main():
    verbose = "--verbose" in sys.argv
    corpus = load("corpus.json")
    eval_data = load("eval_dataset.json")

    retrievers = {"mock": InstrumentedRetriever(MockVectorDB(), top_k=TOP_K)}

    from src.indexer import Indexer  # imported here so the mock runs even without the model
    indexer = Indexer()
    indexer.index_documents(corpus)
    retrievers["embeddings"] = InstrumentedRetriever(
        indexer.vectordb, embeddings=indexer.embeddings, top_k=TOP_K
    )

    results = {name: evaluate(name, r, eval_data, verbose) for name, r in retrievers.items()}

    print(f"\n{len(corpus)} docs | {len(eval_data)} questions | top_k={TOP_K}\n")
    print(f"{'retriever':<12}{'P@'+str(TOP_K):>8}{'R@'+str(TOP_K):>8}{'MRR':>8}{'ms/query':>10}")
    for name, r in results.items():
        print(f"{name:<12}{r['precision']:>8.2f}{r['recall']:>8.2f}{r['mrr']:>8.2f}{r['latency_ms']:>10.2f}")
    print()


if __name__ == "__main__":
    main()
