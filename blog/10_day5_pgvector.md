# Day 5: Moving to a Real Vector Database

**Date:** Oct 8, 2026

## The Decision

Until now my embeddings lived in a Python dictionary that vanished every time the script ended. A real system needs them stored somewhere that persists and that an app can query.

I had two candidates. Weaviate, which I had written code for on Day 2 but never actually run. And Postgres with the pgvector extension, hosted on Supabase. I chose pgvector. DevMind, the app this lab feeds into, will run on Next.js and Supabase, and pgvector is just Postgres: the same table my Python experiments write to can be read by the TypeScript app later. The Weaviate code stays in the repo, honestly labelled as never run.

## The Prediction

A vector database should not change retrieval quality at all. The same embeddings and the same cosine similarity should produce exactly the same rankings, whether the maths runs on my laptop or on a server in Ireland. What should change is speed.

That makes Day 5 a correctness test. If any number moves, something is broken.

## Results (top_k = 3)

| Retriever | Precision@3 | Recall@3 | MRR | ms/query |
|---|---|---|---|---|
| Embeddings, in-memory | 0.40 | 0.93 | 0.78 | 18.79 |
| Embeddings, Supabase pgvector | 0.40 | 0.93 | 0.78 | 696.90 |

Identical quality, to the last decimal. About 37 times slower.

## Where the Time Goes

Searching 14 rows is close to instant for Postgres. Almost all of the 697 ms is the round trip from my laptop in Nigeria to Supabase's servers in Ireland and back. In production that changes: the app's backend would sit in the same region as the database, so the trip shrinks to a few milliseconds. What I measured is the distance between me and the cloud, not pgvector itself.

## What Actually Took Time

Not the code. The connection string.

- Supabase's direct connection needs IPv6, which my network does not have. The Session pooler works over IPv4.
- My password had a `$` in it. Reset it to letters and numbers only.
- The connection string from Supabase has `[YOUR-PASSWORD]` in it. I replaced the words but kept the square brackets. Python then tried to read my password as an IPv6 address, which is how I finally found it.
- Pytest was not loading my `.env` file at all, so the database tests quietly skipped. A two-line `conftest.py` fixed it.

None of that is RAG. All of it is real engineering.

## What I Learned

- Storage should not change results. Proving that it does not is a test worth running.
- Measure where latency comes from before blaming the tool.
- Most of the friction in "add a database" is configuration, not code.

## Next: Day 6

Generation. Retrieval finds the right documents; now Claude has to answer from them, with citations.

---

**Roadmap:** Knowledge base ✅ · Chunking ⬜ · Vector DB ✅ · Retrieval ✅ · Generation ⬜ · Evaluation ⬜
