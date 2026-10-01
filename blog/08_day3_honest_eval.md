# Day 3: A Test That Can Actually Fail

**Date:** Oct 1, 2026

## Why I Rebuilt the Test

My Day 1 numbers came from a mock that ignored the question. My Day 2 test indexed 3 documents and retrieved the top 3, so every query returned everything and precision could never go above 0.33. Neither test could tell a good retriever from a bad one.

So today I built one that can: 14 short documents on RAG concepts, 10 questions, and for each question the IDs of the documents that answer it. The mock stays as a baseline that ignores the question entirely. Anything real has to beat it.

## Results (top_k = 3)

| Retriever | Precision@3 | Recall@3 | MRR | ms/query |
|---|---|---|---|---|
| Mock (ignores query) | 0.10 | 0.30 | 0.18 | 0.01 |
| Embeddings (all-MiniLM-L6-v2) | 0.40 | 0.93 | 0.78 | 18 |
| Best possible on this set | 0.47 | 1.00 | 1.00 | |

## Precision Has a Ceiling

0.40 looked low until I worked out the maximum. Seven questions have one right answer, two have two, one has three. If I always retrieve three documents, the best possible precision is about 0.47. So embeddings reach roughly 85% of what is achievable. A metric means nothing until you know its ceiling.

## Where Embeddings Missed

Recall was 0.93: the right documents almost always made the top 3. The interesting failures are in the ranking (MRR 0.78).

**"What does it mean when the model makes things up?"** The hallucination doc came third, behind the precision and recall docs. The question never uses the word "hallucination", and the docs that ranked higher both talk about "the model" and its context. Semantic search is supposed to handle paraphrase, but a small model still leans on surface overlap.

**"How do I know if retrieval missed relevant documents?"** The RAG overview doc ranked first because it literally says "retrieves relevant documents". The recall doc, which actually answers the question, came second.

**"How does keyword search rank documents?"** The hybrid search doc ranked first because it contains the phrase "keyword search". The BM25 doc, the real answer, came second. Defensible, but not what I labelled.

**"How can I evaluate a whole RAG pipeline?"** The only real recall miss (0.33). Honestly, my labels may be the problem here: I marked the precision and recall docs as relevant, but they describe single metrics, not whole-pipeline evaluation. Labels are judgment calls, and the eval set needs review as much as the retriever does.

## The Cost

Embeddings take about 18 ms per query because every question has to be embedded first. The mock takes 0.01 ms because it does nothing. Fast and wrong is not a feature.

## What I Learned

- A test is only useful if it can fail.
- Know the ceiling before judging a number.
- The misses taught me more than the averages.
- Ground-truth labels are part of the system and can be wrong too.

## Next: Day 4

BM25 keyword search on the same 10 questions. My guess: BM25 wins "how does keyword search rank documents" and loses "makes things up" badly, since that question shares almost no words with its answer. Tomorrow I find out.

---

**Roadmap:** Knowledge base ✅ · Chunking ⬜ · Vector DB 🟡 · Retrieval 🟡 · Generation ⬜ · Evaluation ⬜
