# RAG Learning Journey

Learning retrieval-augmented generation in public over 10 days: build it, measure it, improve it. This repo is the lab for **DevMind**, a RAG assistant for developer docs.

## Run it

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pytest                                  # unit tests (also run in CI)
python -m scripts.run_eval              # compare retrievers on the eval set
python -m scripts.run_eval --verbose    # per-question detail
```

Weaviate needs `WEAVIATE_URL` and `WEAVIATE_API_KEY` in a local `.env` (never committed).

## Structure

```
src/retriever.py          InstrumentedRetriever: timing, precision@k, recall@k, MRR
src/mock_vectordb.py      Query-blind baseline every real retriever must beat
src/embeddings.py         Local embeddings (sentence-transformers, all-MiniLM-L6-v2)
src/in_memory_vectordb.py Cosine similarity search with numpy
src/indexer.py            Embeds documents into the vector store
src/weaviate_db.py        Weaviate Cloud backend
data/corpus.json          14 short docs on RAG concepts
data/eval_dataset.json    10 questions with the doc IDs that answer them
scripts/run_eval.py       Runs every retriever over the eval set
tests/                    pytest suite
blog/                     Learning journal
```

## Results (top_k = 3)

| Retriever | Precision@3 | Recall@3 | MRR |
|---|---|---|---|
| Mock (ignores query) | 0.10 | 0.30 | 0.18 |
| Embeddings (in-memory) | Day 3 | | |
| BM25 | Day 4 | | |

## Progress

- **Day 1:** ✅ Mock retriever and metrics
- **Day 2:** ✅ Real embeddings (sentence-transformers, in-memory) and Weaviate backend
- **Day 3:** Real eval set, tests, CI, first honest embedding numbers
- **Day 4:** BM25 keyword baseline and keywords vs embeddings
- **Day 5:** Choose and wire up the production vector store
- **Day 6:** Generation with Claude, cited answers
- **Day 7:** Hallucination and faithfulness checks
- **Day 8:** Full evaluation with Ragas
- **Day 9:** Improve: chunking, hybrid search or reranking
- **Day 10:** Write-up and hand off to DevMind

## Blog

1. [02_day1_first_test.md](./blog/02_day1_first_test.md) - First test running
2. [03_why_im_building_rag.md](./blog/03_why_im_building_rag.md) - Motivation
3. [04_precision_vs_recall.md](./blog/04_precision_vs_recall.md) - Key insight
4. [05_day1_summary.md](./blog/05_day1_summary.md) - Day 1 recap
5. [06_day2_real_embeddings_plan.md](./blog/06_day2_real_embeddings_plan.md) - Embeddings plan
6. [07_day2_real_embeddings_results.md](./blog/07_day2_real_embeddings_results.md) - Embeddings results
