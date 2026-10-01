from src.mock_vectordb import MockVectorDB


def test_returns_k_results_with_expected_fields():
    results = MockVectorDB().search("anything", k=3)
    assert len(results) == 3
    for r in results:
        assert {"id", "text", "metadata", "score"} <= r.keys()


def test_mock_ignores_the_query():
    db = MockVectorDB()
    assert db.search("embeddings", k=3) == db.search("hallucination", k=3)
