# Understanding Precision vs Recall: My First Aha Moment

**Date:** Sept 29, 2026

## The Test

I ran my retriever on the question: "What is an embedding?"

Result:

Metrics:
- **Precision: 0.50**
- **Recall: 1.00**

## What This Means

### Precision = 0.50 (50%)

"Of the 2 documents I retrieved, only 1 was actually relevant."

**In other words:** I had noise. retrieval.txt wasn't needed.

### Recall = 1.00 (100%)

"I found all the relevant documents that exist."

**In other words:** I didn't miss anything important.

## The Tradeoff

This is the key insight:

**To get Recall = 1.00, I had to sacrifice Precision**

If I only retrieved 1 document:
- Precision = 1.00 (perfect, no noise)
- Recall = 1.00 (found the one relevant doc)

But what if there were 2 relevant docs and I only retrieved 1?
- Precision = 1.00 (both I retrieved were good)
- Recall = 0.50 (missed one relevant doc)

**You can't have both 100% without luck.**

## Real World Impact

### High Precision (low recall)
Retriever is picky. Only returns docs you're sure about.
- ✅ Context is clean
- ✅ LLM won't get confused
- ❌ Might miss important info

### High Recall (low precision)
Retriever is generous. Returns everything possibly relevant.
- ✅ Won't miss important info
- ✅ More context to work with
- ❌ LLM has to wade through noise

## What I Learned

**There's no magic number.** You have to choose based on your use case:
- Customer support? → High precision (no wrong answers)
- Research? → High recall (find everything)
- General QA? → Balance both

This is **real engineering thinking.** Not "maximize both."

---

Next post: What happens when I get real embeddings?
