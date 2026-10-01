"""Check the metric maths with a fake DB whose ranking we control."""
import pytest

from src.retriever import InstrumentedRetriever


class FixedOrderDB:
    def __init__(self, ids):
        self.ids = ids

    def search(self, query, k=5):
        return [{"id": i, "text": "", "metadata": {}, "score": 1.0} for i in self.ids[:k]]


def run(ids, ground_truth, k=3):
    retriever = InstrumentedRetriever(FixedOrderDB(ids), top_k=k)
    _, metrics = retriever.retrieve("q", ground_truth_doc_ids=ground_truth)
    return metrics


def test_perfect_retrieval():
    m = run(["a", "b", "c"], ["a", "b", "c"])
    assert m.precision_at_k == 1.0
    assert m.recall_at_k == 1.0
    assert m.mrr == 1.0


def test_one_relevant_doc_at_rank_two():
    m = run(["x", "a", "y"], ["a"])
    assert m.precision_at_k == pytest.approx(1 / 3)
    assert m.recall_at_k == 1.0
    assert m.mrr == 0.5


def test_missed_relevant_doc_lowers_recall():
    m = run(["a", "x", "y"], ["a", "b"])
    assert m.recall_at_k == 0.5
    assert m.mrr == 1.0


def test_nothing_relevant():
    m = run(["x", "y", "z"], ["a"])
    assert m.precision_at_k == 0.0
    assert m.recall_at_k == 0.0
    assert m.mrr == 0.0


def test_metrics_are_logged():
    retriever = InstrumentedRetriever(FixedOrderDB(["a"]), top_k=1)
    retriever.retrieve("q1", ground_truth_doc_ids=["a"])
    retriever.retrieve("q2", ground_truth_doc_ids=["a"])
    assert len(retriever.metrics_log) == 2
