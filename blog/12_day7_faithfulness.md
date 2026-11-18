# Day 7: Is My RAG Telling the Truth?

**Date:** Nov 18, 2026

## Picking Up Where I Left Off

Day 6 ended with an uncomfortable find. My script reported 0 made-up citations, and that was true. But one answer cited a real document for a claim that document never makes:

> *"If you notice recall is low, you might improve retrieval by using reranking [reranking]."*

The reranking doc says reranking *reorders* documents that were already retrieved. It says nothing about fixing low recall. Day 6 checked that citations **exist**. Day 7 checks that they are **true**.

## What I Built

`src/faithfulness.py` takes every Day 6 answer and:

1. **Splits it into claims.** One sentence is one claim, and each keeps the ids it cites.
2. **Looks up the cited source.** Only the cited one, not all three retrieved docs. A claim has to be backed by the source it points to.
3. **Scores each claim two ways:**
   - **Word overlap.** What share of the claim's meaningful words appear in the source? Free and instant.
   - **Claude as a judge.** Haiku reads the source and the claim (citation removed) and answers `supported`, `partial` or `unsupported`, with a one-sentence reason. It is told to judge only against the source, even if the claim is true in the real world.

An answer's **faithfulness** is the share of its claims that are fully supported. Refusals are skipped, since "I don't know" makes no claim.

It reads `results/day6_generation.json`, so there is no retrieval and no embedding model to load. It runs in seconds, even on my old Mac.

## Result 1: Word Overlap Is Fooled Both Ways

18 claims across the 9 answered questions. Overlap called a claim supported if at least 60% of its words were in the source.

| | Overlap says |
|---|---|
| Supported | 15 / 18 |
| Not supported | 3 / 18 |
| Average faithfulness | 0.83 |

That looks fine until you read the 3 it flagged:

| Claim | Overlap | Really? |
|---|---|---|
| "When a model makes things up, it's called a hallucination" | 0.40 | Faithful. The source says "states something that is not supported", not "makes things up". |
| "Chunking helps achieve an optimal balance where the pieces are large enough to preserve context..." | 0.43 | A fair paraphrase of "too large dilutes, too small loses context". Arguably faithful. |
| "Precision at k tells you how much noise is in your retrieved results" | 0.50 | Faithful. The source says "low precision means the context contains noise". |

All three are paraphrases, and overlap punished them for using different words.

And the reranking sentence, the one claim I *know* is unfaithful? **Overlap 0.62. Passed.** It borrows the source's words ("reranking", "reorders", "retrieved documents", "LLM") and wraps them around an idea the source never states.

Word overlap measures how much an answer *sounds like* its source, not whether it *says the same thing*. It flags honest paraphrases and passes confident misreadings.

## Result 2: The Judge Passed Everything, Including the Bad One

| | Judge says |
|---|---|
| Supported | 18 / 18 |
| Partial | 0 / 18 |
| Unsupported | 0 / 18 |
| Agrees with overlap | 15 / 18 |
| Fully faithful answers | 9 / 9 |
| Average faithfulness | 1.00 |
| Tokens in / out | 3,876 / 918 |

The good news: the judge cleared all three paraphrases that word overlap wrongly flagged. It understands that "makes things up" and "states something not supported" mean the same thing. Overlap can't.

The bad news: it also called the reranking sentence **supported**.

> *"If you notice recall is low, you might improve retrieval by using reranking, which reorders retrieved documents with a more accurate model before sending them to the LLM [reranking]."*

Most of that sentence *is* in the source: what reranking is, what it does, and that it happens before the LLM. The one unsupported idea, that reranking is a fix for low recall, is a single hedged clause at the front ("you might"). The judge read the sentence as a whole, found it mostly true, and passed it.

So both checks missed the same claim, for different reasons:

- **Word overlap** passed it because it uses the source's words.
- **The judge** passed it because most of it is true.

A faithfulness score of 1.00 sounds like proof. Here it hides the one unfaithful sentence I found by reading.

## Why I Think the Judge Missed It

1. **Sentences are too big.** That sentence holds two claims: "reranking reorders documents with a better model" (supported) and "reranking helps when recall is low" (not supported). Judged together, the true part carries the false one. This is why tools like Ragas break answers into single, atomic statements before checking them.
2. **Hedges soften claims.** "You might improve retrieval" sounds like a suggestion, not a fact, so it is easy to let through.
3. **Haiku is grading Haiku.** The judge is the same model that wrote the answer, so it may share the same idea of what is a reasonable thing to say.

## Caveats

- **18 claims is a tiny sample.** These numbers describe my 14-doc corpus, not RAG in general.
- **One known bad claim** is all I have to test against. I found it by hand. There may be others neither check caught.

## What I Learned

- Valid citations, Day 6's check, are necessary but not enough.
- Word overlap is a poor stand-in for meaning. It fails in both directions.
- An LLM judge understands paraphrase, but judging a whole sentence lets a false clause hide behind true ones.
- A perfect score is a reason to look harder, not to stop. Reading outputs by hand found the one problem both automated checks missed.

## Next: Day 8

Ragas. Its faithfulness metric first breaks each answer into atomic statements, then checks each one. The test is simple: does it catch the reranking claim that my sentence-level judge let through?

---

**Roadmap:** Knowledge base ✅ · Chunking ⬜ · Vector DB ✅ · Retrieval ✅ · Generation ✅ · Evaluation 🟡
