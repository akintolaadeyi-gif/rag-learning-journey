"""Guard the eval set: every expected doc must exist in the corpus."""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def load(name):
    with open(DATA / name) as f:
        return json.load(f)


def test_corpus_ids_are_unique():
    ids = [d["id"] for d in load("corpus.json")]
    assert len(ids) == len(set(ids))


def test_every_relevant_doc_exists_in_corpus():
    corpus_ids = {d["id"] for d in load("corpus.json")}
    for item in load("eval_dataset.json"):
        missing = set(item["relevant_doc_ids"]) - corpus_ids
        assert not missing, f"{item['question']!r} points at unknown docs: {missing}"


def test_every_question_has_at_least_one_relevant_doc():
    for item in load("eval_dataset.json"):
        assert item["relevant_doc_ids"], item["question"]
