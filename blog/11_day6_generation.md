# Day 6: Letting Claude Answer

**Date:** Nov 2, 2026

## What I Built

Until today my system could find the right documents but could not say anything. Day 6 adds the last letter of RAG: generation. The top 3 retrieved documents go to Claude (Haiku 4.5) with four rules:

1. Answer only from the provided sources.
2. Put the source id in square brackets after every claim, e.g. `[bm25]`.
3. Never use outside knowledge, even if you know the answer.
4. If the sources do not contain the answer, say exactly "I don't know based on the provided documents."

Then a script checks every answer mechanically: did it answer or refuse, which ids did it cite, and did it cite anything that was not in the sources (a made-up citation)?

To test rule 3, I added three trick questions with no answer in the corpus (`data/unanswerable.json`), each designed to tempt the model in a different way:

- **"What is the capital of France?"** Claude knows this. The corpus does not.
- **"How much does Pinecone cost per month?"** Pinecone is mentioned in the corpus, but no price is. A partial match that invites guessing.
- **"Which embedding model has the most dimensions?"** On topic for RAG, but the corpus never compares models.

## Results (top_k = 3, 10 real questions + 3 trick questions)

| Check | Result |
|---|---|
| Answerable questions answered | 9 / 10 |
| ...citing at least one correct doc | 9 / 9 |
| Trick questions refused | 3 / 3 |
| Made-up citations | 0 |
| Tokens in / out | 3,618 / 764 |
| Average latency | 1.4 s per answer |

The whole run cost a fraction of a cent.

## The Miss: Too Careful, Not Too Creative

The one failure was not a hallucination. It was the opposite.

For "How can I evaluate a whole RAG pipeline?", retrieval did its job and put the Ragas doc first. Claude read it and answered: *"I don't know based on the provided documents."* Its reasoning was that the doc names Ragas and what it measures but does not describe a full evaluation process.

That is **over-refusal**. A strict "sources only" prompt makes the model safer, but it also makes it timid when the source is short. Every RAG prompt sits somewhere on this dial between making things up and refusing things it could answer, and I now have one data point for where mine sits.

## The Thing My Checks Did Not Catch

My script says 0 made-up citations, and that is true. But reading the answers by hand, I found one that cites a real source for a claim that source does not make.

For "How do I know if retrieval missed relevant documents?", Claude correctly explained recall at k, then added: *"If you notice recall is low, you might improve retrieval by using reranking [reranking]."* The reranking doc says reranking *reorders* documents that were already retrieved. It says nothing about fixing low recall, and reordering alone cannot bring back a document that was never retrieved.

The citation is real. The claim is not supported by it. A mechanical check can confirm that `[reranking]` exists; it cannot confirm that the sentence before it is true to the source. That gap is exactly what Day 7 is about.

## Smaller Things I Noticed

- **"Say exactly" is not exact.** On every refusal, Claude gave the required sentence and then added an explanation. My refusal check looks for the sentence anywhere in the answer, so it still counted, but an instruction like "reply with exactly" is a strong suggestion, not a guarantee.
- **A fake only tests what you told it to expect.** All my unit tests passed against a fake Claude, and the first real call still failed because the code sent a setting the real API no longer accepts.
- **Most of the day was setup, again.** A workspace-scoped API key, a credit balance sitting on a different key than the one in my `.env`, and a PyTorch install that had quietly broken inside my virtual environment. None of that is RAG. All of it is real.

## What I Learned

- Generation quality has two failure directions: inventing things and refusing things. Measure both.
- Valid citations are not the same as faithful answers.
- Reading the actual outputs by hand found something my metrics missed.

## Next: Day 7

Faithfulness. Check every claim in every answer against the source it cites, starting with the reranking sentence above.

---

**Roadmap:** Knowledge base ✅ · Chunking ⬜ · Vector DB ✅ · Retrieval ✅ · Generation ✅ · Evaluation ⬜
