"""
FAITHFULNESS
Checks whether each claim in an answer is actually backed by the source it cites.

Day 6 checked that citations EXIST. Day 7 checks that they are TRUE:
  1. Split the answer into claims (one sentence = one claim) with the ids it cites.
  2. Look up the text of each cited source.
  3. Score the claim against that text two ways:
       - word overlap: free and instant, but only sees shared words
       - Claude as a judge: reads the source and says supported / partial / unsupported

An answer's faithfulness = share of its claims that are fully supported.
"""
import json
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.generator import DEFAULT_MODEL, is_refusal, parse_citations

VERDICTS = ("supported", "partial", "unsupported")

# Words too common to say anything about whether a source backs a claim
STOPWORDS = set("""
a an the and or but if then so to of in on at by for with from into as is are was were be been being
it its this that these those there their they them you your we our i me my he she his her
can could may might will would should do does did not no yes than too very just also
which who whom what when where why how all any each more most other some such only own same
about over under again further once here both few between through during before after above below
up down out off use used using means mean helps help
""".split())


@dataclass
class Claim:
    text: str
    cited_ids: List[str]
    overlap: float = 0.0             # share of the claim's content words found in its sources
    overlap_verdict: str = ""        # supported / unsupported, from overlap alone
    judge_verdict: str = ""          # supported / partial / unsupported, from Claude
    judge_reason: str = ""


@dataclass
class AnswerCheck:
    question: str
    answer: str
    refused: bool
    claims: List[Claim] = field(default_factory=list)

    @property
    def faithfulness(self) -> Optional[float]:
        """Share of claims the judge (or, without a judge, overlap) calls fully supported."""
        if not self.claims:
            return None
        ok = [c for c in self.claims if (c.judge_verdict or c.overlap_verdict) == "supported"]
        return len(ok) / len(self.claims)


# ---------- 1. split an answer into claims ----------

def split_claims(answer: str) -> List[Claim]:
    """One sentence = one claim. Markdown bold is removed; citations stay attached to their sentence."""
    text = answer.replace("**", "").strip()
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
    claims = []
    for s in sentences:
        s = s.strip()
        if not s or is_refusal(s):
            continue
        claims.append(Claim(text=s, cited_ids=parse_citations(s)))
    return claims


def strip_citations(text: str) -> str:
    return re.sub(r"\s*\[[A-Za-z0-9_.\-]+\]", "", text).strip()


# ---------- 2a. word overlap ----------

def content_words(text: str) -> List[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [stem(w) for w in words if w not in STOPWORDS and len(w) > 2]


def stem(word: str) -> str:
    """Very rough: 'documents' -> 'document', 'ranks' -> 'rank', 'reorders' -> 'reorder'."""
    for suffix in ("ing", "es", "ed", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[: -len(suffix)]
    return word


def overlap_score(claim: str, sources: List[str]) -> float:
    claim_words = content_words(strip_citations(claim))
    if not claim_words:
        return 1.0
    source_words = set(content_words(" ".join(sources)))
    return sum(w in source_words for w in claim_words) / len(claim_words)


# ---------- 2b. Claude as a judge ----------

JUDGE_PROMPT = """You check whether a claim is supported by a source text.

Verdicts:
- supported: everything the claim says is stated in the source or follows directly from it.
- partial: some of the claim is in the source, but it adds something the source does not say.
- unsupported: the source does not say this, or says something different.

Judge only against the source text. Do not use outside knowledge, even if the claim is true in the real world.
Reply with JSON only, no other text: {"verdict": "supported" | "partial" | "unsupported", "reason": "<one sentence>"}"""


def parse_verdict(reply: str) -> Dict[str, str]:
    """Pull the JSON object out of the judge's reply, tolerating code fences or extra text."""
    match = re.search(r"\{.*\}", reply, re.DOTALL)
    try:
        data = json.loads(match.group(0)) if match else {}
    except json.JSONDecodeError:
        data = {}
    verdict = str(data.get("verdict", "")).lower().strip()
    if verdict not in VERDICTS:
        return {"verdict": "unparsed", "reason": reply.strip()[:200]}
    return {"verdict": verdict, "reason": str(data.get("reason", "")).strip()}


class ClaudeJudge:
    def __init__(self, model: str = None, client=None):
        self.model = model or os.getenv("CLAUDE_MODEL", DEFAULT_MODEL)
        if client is None:
            import anthropic  # imported here so tests and CI never need it
            client = anthropic.Anthropic()
        self.client = client
        self.input_tokens = 0
        self.output_tokens = 0

    def judge(self, claim: str, sources: Dict[str, str]) -> Dict[str, str]:
        source_block = "\n".join(f'<source id="{sid}">{text}</source>' for sid, text in sources.items())
        response = self.client.messages.create(
            model=self.model,
            max_tokens=200,
            system=JUDGE_PROMPT,
            messages=[{"role": "user", "content": f"{source_block}\n\nClaim: {strip_citations(claim)}"}],
        )
        self.input_tokens += response.usage.input_tokens
        self.output_tokens += response.usage.output_tokens
        reply = "".join(b.text for b in response.content if getattr(b, "type", "text") == "text")
        return parse_verdict(reply)


# ---------- 3. check a whole answer ----------

def check_answer(record: Dict, corpus: Dict[str, str], judge: ClaudeJudge = None,
                 overlap_threshold: float = 0.6) -> AnswerCheck:
    """record is one entry of results/day6_generation.json; corpus maps doc id -> text."""
    check = AnswerCheck(question=record["question"], answer=record["answer"], refused=record["refused"])
    if record["refused"]:
        return check  # a refusal makes no claims to check

    for claim in split_claims(record["answer"]):
        sources = {cid: corpus[cid] for cid in claim.cited_ids if cid in corpus}
        if not sources:
            claim.overlap_verdict = "uncited"
            if judge:
                claim.judge_verdict, claim.judge_reason = "unsupported", "No valid citation."
            check.claims.append(claim)
            continue
        claim.overlap = overlap_score(claim.text, list(sources.values()))
        claim.overlap_verdict = "supported" if claim.overlap >= overlap_threshold else "unsupported"
        if judge:
            v = judge.judge(claim.text, sources)
            claim.judge_verdict, claim.judge_reason = v["verdict"], v["reason"]
        check.claims.append(claim)
    return check
