"""Cosine search with hand-made vectors, so no model download is needed."""
import pytest

from src.in_memory_vectordb import InMemoryVectorDB


def make_db():
    db = InMemoryVectorDB()
    db.add_document("north", "points north", [0.0, 1.0])
    db.add_document("east", "points east", [1.0, 0.0])
    db.add_document("north_east", "points north-east", [1.0, 1.0])
    return db


def test_closest_vector_ranks_first():
    results = make_db().search([0.1, 1.0], k=3)
    assert [r["id"] for r in results] == ["north", "north_east", "east"]


def test_identical_direction_scores_one():
    results = make_db().search([0.0, 5.0], k=1)
    assert results[0]["score"] == pytest.approx(1.0)


def test_k_limits_results():
    assert len(make_db().search([1.0, 0.0], k=2)) == 2
