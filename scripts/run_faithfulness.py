"""
Day 7: check every claim in the Day 6 answers against the source it cites.

Usage (from the project root):
    python -m scripts.run_faithfulness              # word overlap + Claude judge (needs ANTHROPIC_API_KEY in .env)
    python -m scripts.run_faithfulness --no-judge   # word overlap only: free, no key, no network

Reads results/day6_generation.json, so there is no retrieval and no embedding model
to load: it only needs the anthropic and python-dotenv packages.
Saves everything to results/day7_faithfulness.json.
"""
import argparse
import json
from dataclasses import asdict
from pathlib import Path

from dotenv import load_dotenv

from src.faithfulness import ClaudeJudge, check_answer

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-judge", action="store_true", help="word overlap only, no Claude calls")
    args = parser.parse_args()

    corpus = {d["id"]: d["text"] for d in json.loads((ROOT / "data" / "corpus.json").read_text())}
    records = json.loads((ROOT / "results" / "day6_generation.json").read_text())
    judge = None if args.no_judge else ClaudeJudge()
    if judge:
        print(f"\nJudge: {judge.model}\n")

    checks = [check_answer(r, corpus, judge) for r in records]

    for c in checks:
        if c.refused:
            continue
        print(c.question)
        for cl in c.claims:
            judged = f"judge={cl.judge_verdict:<11} " if judge else ""
            print(f"  overlap={cl.overlap:.2f} ({cl.overlap_verdict:<11}) {judged}{cl.text}")
            if cl.judge_verdict and cl.judge_verdict != "supported":
                print(f"      why: {cl.judge_reason}")
        print()

    claims = [cl for c in checks for cl in c.claims]
    answers = [c for c in checks if c.claims]

    def count(attr, verdict):
        return sum(getattr(cl, attr) == verdict for cl in claims)

    print("Summary")
    print(f"  Answers checked:                {len(answers)} ({sum(c.refused for c in checks)} refusals skipped)")
    print(f"  Claims checked:                 {len(claims)}")
    print(f"  Word overlap says supported:    {count('overlap_verdict', 'supported')}/{len(claims)}")
    if judge:
        for v in ("supported", "partial", "unsupported", "unparsed"):
            if count("judge_verdict", v) or v != "unparsed":
                print(f"  Judge says {v + ':':<20}{count('judge_verdict', v)}/{len(claims)}")
        agree = sum((cl.overlap_verdict == "supported") == (cl.judge_verdict == "supported") for cl in claims)
        print(f"  Overlap and judge agree:        {agree}/{len(claims)}")
        print(f"  Fully faithful answers:         {sum(c.faithfulness == 1.0 for c in answers)}/{len(answers)}")
        print(f"  Judge tokens in / out:          {judge.input_tokens} / {judge.output_tokens}")
    avg = sum(c.faithfulness for c in answers) / len(answers)
    print(f"  Average faithfulness:           {avg:.2f}\n")

    out = ROOT / "results" / ("day7_faithfulness.json" if judge else "day7_overlap_only.json")
    out.write_text(json.dumps([{**asdict(c), "faithfulness": c.faithfulness} for c in checks], indent=2))
    print(f"Saved {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
