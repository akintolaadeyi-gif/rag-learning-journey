# Day 2: Real Embeddings - The Precision-Recall Tradeoff in Action

**Date:** Oct 5, 2026

## What Changed

Day 1: Mock database with fake similarity scores  
Day 2: Real embeddings with semantic search

## The Test

Query: "What is an embedding?"

### Day 1 Results (Mock)

### Day 2 Results (Real Embeddings)
## What I Learned

### The Real Tradeoff

With real embeddings:
- **Better ranking:** sample.txt ranked #1 (correct!)
- **Lower precision:** Only 1/3 retrieved docs were marked relevant
- **Higher false positives:** retrieval.txt matched because it says "embeddings"

### Why This Matters

Real embeddings don't just do keyword matching—they understand **semantic meaning**. 

"embeddings" in retrieval.txt is semantically similar to my query, so it matched. That's not wrong, it's how embeddings work.

### The Engineering Decision

Do I:
- Increase `top_k` (retrieve more docs, lower precision)?
- Decrease `top_k` (fewer docs, higher precision)?
- Change the embedding model (different tradeoffs)?

This is **real engineering thinking**. It's not about "getting it right." It's about understanding tradeoffs and choosing what matters for your use case.

## Technical Details

- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **Dimensions:** 384
- **Similarity:** Cosine similarity
- **Database:** In-memory (free, local)

## Next Steps

Day 3: Add LLM generation and measure hallucinations.

---

**Status:** Foundation solid ✅  
**Learning:** Real tradeoffs, not theory  
**Code:** Working retriever with real embeddings
