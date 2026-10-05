# Day 4: Keywords vs Meaning

**Date:** Oct 1, 2026

## What I Built

BM25 keyword search, written from scratch in about 40 lines (`src/bm25_db.py`). No library, so I could see exactly why each document scores what it scores. For every word a question shares with a document, BM25 adds up three things: how rare the word is across all documents, how often it appears in this one (with diminishing returns), and a small penalty for long documents.

What it cannot do: understand meaning. "Rank" and "ranking" are as different to BM25 as "rank" and "banana".

## Results (top_k = 3, same 10 questions)

| Retriever | Precision@3 | Recall@3 | MRR | ms/query |
|---|---|---|---|---|
| Mock | 0.10 | 0.30 | 0.18 | 0.01 |
| BM25 | 0.33 | 0.78 | 0.72 | 0.19 |
| Embeddings | 0.40 | 0.93 | 0.78 | 20.77 |
| Best possible | 0.47 | 1.00 | 1.00 | |

Embeddings win on every quality metric. BM25 gets most of the way there at about 100 times the speed.

## My Predictions

On Day 3 I made two predictions.

**"BM25 will fail 'what does it mean when the model makes things up?'" Correct, and the reason was funnier than I expected.** After dropping filler words, the question becomes: mean, model, makes, things, up. BM25 ranked the Ragas doc first because it says "measures **things** like". The embeddings doc came second because it says "end **up**". The MRR doc came third because it starts with "**Mean** reciprocal rank". The hallucination doc does contain "model", but that word appears in five documents, so BM25 treats it as nearly worthless. Pure word counting, zero understanding.

**"BM25 will win 'how does keyword search rank documents?'" Wrong.** It did worse than embeddings. The BM25 doc says "ranking", not "rank", so it got no credit for that word. The MRR doc says "rank" three times ("rank 1, rank 2, rank 3") and jumped ahead of it.

## Where BM25 Beat Embeddings

"Where are embeddings stored and searched?" BM25 ranked the vector database doc first; embeddings ranked it second. Same literalism, working in BM25's favour this time: only the vector database doc contains the exact plural "embeddings".

## What I Learned

Almost every BM25 miss came down to word forms: rank vs ranking, embedding vs embeddings, mean vs meaning. The standard fix is stemming, which reduces words to their root. I am not adding it yet. If I tune BM25 until it scores well on these exact 10 questions, I am tuning to the test, not improving search. That is what a held-out test set is for, and I still need to write one.

The bigger lesson: the two methods fail on different questions. Embeddings get distracted by shared phrases. BM25 is blind to meaning but fast and exact. Combining them is called hybrid search, and now I have a measured reason to try it.

## Next: Day 5

Choosing the production vector store. My Weaviate code exists but has never actually run, so this is a real decision, not a formality.

---

**Roadmap:** Knowledge base ✅ · Chunking ⬜ · Vector DB 🟡 · Retrieval ✅ · Generation ⬜ · Evaluation ⬜
