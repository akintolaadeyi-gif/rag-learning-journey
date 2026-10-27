"""
Day 6: retrieve with embeddings, answer with Claude, check the answers.

Usage (from the project root):
    python -m scripts.run_generation

Needs ANTHROPIC_API_KEY in .env. Saves everything to results/day6_generation.json.
"""
import json
from dataclasses import asdict
from pathlib import Path

from dotenv import load_dotenv

from src.generator import ClaudeGenerator
from src.retriever import InstrumentedRetriever

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
TOP_K = 3


def load(name):
    with open(ROOT / "data" / name) as f:
        return json.load(f)


def main():
    corpus = load("corpus.json")
    answerable = load("eval_dataset.json")
    unanswerable = load("unanswerable.json")

    from src.indexer import Indexer
    indexer = Indexer()
    indexer.index_documents(corpus, verbose=False)
    retriever = InstrumentedRetriever(indexer.vectordb, embeddings=indexer.embeddings, top_k=TOP_K)
    generator = ClaudeGenerator()
    print(f"\nModel: {generator.model} | top_k={TOP_K}\n")

    records = []
    questions = [(q["question"], q["relevant_doc_ids"], True) for q in answerable] + \
                [(q["question"], [], False) for q in unanswerable]

    for question, relevant, should_answer in questions:
        docs, _ = retriever.retrieve(question)
        g = generator.generate(question, docs)
        cites_relevant = bool(set(g.cited_ids) & set(relevant))
        record = {**asdict(g), "should_answer": should_answer, "relevant_doc_ids": relevant,
                  "cites_relevant_doc": cites_relevant}
        records.append(record)

        tag = "ANSWERABLE  " if should_answer else "UNANSWERABLE"
        print(f"[{tag}] {question}")
        print(f"    retrieved: {g.source_ids}")
        print(f"    answer:    {g.answer}")
        flags = []
        if g.invalid_citations:
            flags.append(f"MADE-UP CITATION {g.invalid_citations}")
        if should_answer and g.refused:
            flags.append("refused an answerable question")
        if not should_answer and not g.refused:
            flags.append("ANSWERED AN UNANSWERABLE QUESTION")
        if should_answer and not g.refused and not g.cited_ids:
            flags.append("no citations")
        print(f"    check:     {'; '.join(flags) if flags else 'ok'}\n")

    ans = [r for r in records if r["should_answer"]]
    unans = [r for r in records if not r["should_answer"]]
    answered = [r for r in ans if not r["refused"]]

    print("Summary")
    print(f"  Answerable questions answered:      {len(answered)}/{len(ans)}")
    print(f"  ...citing at least one right doc:   {sum(r['cites_relevant_doc'] for r in answered)}/{len(answered)}")
    print(f"  Unanswerable questions refused:     {sum(r['refused'] for r in unans)}/{len(unans)}")
    print(f"  Made-up citations:                  {sum(len(r['invalid_citations']) for r in records)}")
    print(f"  Tokens in / out:                    {sum(r['input_tokens'] for r in records)} / {sum(r['output_tokens'] for r in records)}")
    print(f"  Avg generation latency:             {sum(r['latency_ms'] for r in records) / len(records):.0f} ms\n")

    out = ROOT / "results" / "day6_generation.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(records, indent=2))
    print(f"Saved {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
