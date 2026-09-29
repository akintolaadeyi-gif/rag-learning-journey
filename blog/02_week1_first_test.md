# Week 1: My First RAG Retriever Test - It Works!

**Date:** Sept 29, 2026

## What I Did

1. Set up Python virtual environment
2. Installed dependencies 
3. Created mock vector database
4. Created instrumented retriever
5. Tested it with real metrics

## What Happened

I ran the retriever on the question "What is an embedding?"

**Results:**
- Retrieved 2 documents
- Precision: 0.50 (50% of retrieved docs were relevant)
- Recall: 1.00 (found all relevant docs)
- MRR: 1.00 (found relevant doc at position 1)

## What I Learned

**The Precision-Recall Tradeoff:**
- I retrieved 2 documents, but only 1 was relevant
- This gave me Precision = 0.50
- But I found all relevant docs, so Recall = 1.00
- This is the real tradeoff: retrieve more to not miss anything, but get noise

## What's Next

- Test with more questions
- Get real embeddings working
- See how precision/recall change with real data

---

**Code working:** ✅  
**Metrics working:** ✅  
**Learning:** Just starting
