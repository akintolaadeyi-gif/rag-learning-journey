"""
GENERATOR
Turns retrieved documents into an answer with Claude.

The rules Claude gets:
  1. Answer only from the provided sources.
  2. Cite the source id in square brackets after each claim, e.g. [bm25].
  3. If the sources do not contain the answer, say exactly IDK_ANSWER.

We then check the answer mechanically: which ids were cited, whether any
cited id was NOT in the sources (a made-up citation), and whether it refused.
"""
import os
import re
import time
from dataclasses import dataclass, field
from typing import Dict, List

DEFAULT_MODEL = "claude-haiku-4-5-20251001"
IDK_ANSWER = "I don't know based on the provided documents."

SYSTEM_PROMPT = f"""You answer questions using ONLY the sources provided in the user message.

Rules:
- Every factual claim must be followed by the id of the source it came from, in square brackets, e.g. [bm25].
- Only cite ids that appear in the sources.
- Do not use outside knowledge, even if you know the answer.
- If the sources do not contain the answer, reply with exactly: {IDK_ANSWER}
- Keep answers to 1 to 3 sentences."""


@dataclass
class Generation:
    question: str
    answer: str
    source_ids: List[str]
    cited_ids: List[str] = field(default_factory=list)
    invalid_citations: List[str] = field(default_factory=list)
    refused: bool = False
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0


def build_user_message(question: str, documents: List[Dict]) -> str:
    sources = "\n".join(f'<source id="{d["id"]}">{d["text"]}</source>' for d in documents)
    return f"<sources>\n{sources}\n</sources>\n\nQuestion: {question}"


def parse_citations(answer: str) -> List[str]:
    """All [ids] in the answer, in order of first appearance, no duplicates."""
    seen = []
    for cid in re.findall(r"\[([A-Za-z0-9_.\-]+)\]", answer):
        if cid not in seen:
            seen.append(cid)
    return seen


def is_refusal(answer: str) -> bool:
    return IDK_ANSWER.lower().rstrip(".") in answer.lower()


class ClaudeGenerator:
    def __init__(self, model: str = None, client=None, max_tokens: int = 300):
        self.model = model or os.getenv("CLAUDE_MODEL", DEFAULT_MODEL)
        self.max_tokens = max_tokens
        if client is None:
            import anthropic  # imported here so tests and CI never need it
            client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
        self.client = client

    def generate(self, question: str, documents: List[Dict]) -> Generation:
        start = time.time()
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_user_message(question, documents)}],
        )
        latency = (time.time() - start) * 1000

        answer = "".join(block.text for block in response.content if getattr(block, "type", "text") == "text").strip()
        source_ids = [d["id"] for d in documents]
        cited = parse_citations(answer)

        return Generation(
            question=question,
            answer=answer,
            source_ids=source_ids,
            cited_ids=cited,
            invalid_citations=[c for c in cited if c not in source_ids],
            refused=is_refusal(answer),
            model=self.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            latency_ms=latency,
        )
