import json

import pytest

from src.bm25_db import BM25DB, tokenize


@pytest.fixture
def db(tmp_path):
    corpus = [
        {"id": "cats", "text": "Cats sleep a lot. Cats like fish."},
        {"id": "dogs", "text": "Dogs like walks and fetch."},
        {"id": "fish", "text": "Fish swim in water."},
    ]
    path = tmp_path / "corpus.json"
    path.write_text(json.dumps(corpus))
    return BM25DB(corpus_path=path)


def test_tokenize_lowercases_and_drops_stopwords():
    assert tokenize("What IS the BM25 score?") == ["bm25", "score"]


def test_matching_document_ranks_first(db):
    assert db.search("sleeping cats", k=1)[0]["id"] == "cats"


def test_no_shared_words_scores_zero(db):
    assert all(r["score"] == 0 for r in db.search("quantum physics", k=3))


def test_rare_word_outweighs_common_word(db):
    # "like" is in two docs, "swim" in one, so "swim" should decide the winner
    assert db.search("like swim", k=1)[0]["id"] == "fish"


def test_k_limits_results(db):
    assert len(db.search("fish", k=2)) == 2
