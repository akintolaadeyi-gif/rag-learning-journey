"""
Runs only when DATABASE_URL is set (skipped in CI).
Uses its own small table with 2-dimensional vectors, so real data is untouched.
"""
import os

import pytest

pytestmark = pytest.mark.skipif(not os.getenv("DATABASE_URL"), reason="DATABASE_URL not set")


@pytest.fixture
def db():
    from src.pgvector_db import PgVectorDB
    store = PgVectorDB(table="test_documents", dim=2)
    store.drop()
    store = PgVectorDB(table="test_documents", dim=2)
    store.add_document("north", "points north", [0.0, 1.0])
    store.add_document("east", "points east", [1.0, 0.0])
    store.add_document("north_east", "points north-east", [1.0, 1.0])
    yield store
    store.drop()


def test_closest_vector_ranks_first(db):
    assert [r["id"] for r in db.search([0.1, 1.0], k=3)] == ["north", "north_east", "east"]


def test_identical_direction_scores_one(db):
    assert db.search([0.0, 5.0], k=1)[0]["score"] == pytest.approx(1.0)


def test_reindexing_updates_instead_of_duplicating(db):
    db.add_document("north", "still north", [0.0, 1.0])
    assert db.count() == 3
