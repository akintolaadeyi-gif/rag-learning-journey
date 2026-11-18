"""Faithfulness tests with a fake Claude judge: no API key, no network, no cost."""
from types import SimpleNamespace

from src.faithfulness import (ClaudeJudge, check_answer, overlap_score,
                              parse_verdict, split_claims)
from src.generator import IDK_ANSWER

CORPUS = {
    "reranking": "Reranking takes the first batch of retrieved documents and reorders them "
                 "with a slower, more accurate model before sending them to the LLM.",
    "recall_at_k": "Recall at k is the share of all relevant documents that appear in the top k results.",
}


class FakeJudgeClient:
    def __init__(self, reply):
        self.reply = reply
        self.calls = []
        self.messages = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=self.reply)],
                               usage=SimpleNamespace(input_tokens=50, output_tokens=10))


def record(answer, refused=False):
    return {"question": "q", "answer": answer, "refused": refused}


def test_split_claims_keeps_citations_with_their_sentence():
    claims = split_claims("Recall counts hits [recall_at_k]. **Reranking** reorders [reranking].")
    assert [c.cited_ids for c in claims] == [["recall_at_k"], ["reranking"]]
    assert "**" not in claims[1].text


def test_split_claims_skips_the_refusal_sentence():
    assert split_claims(IDK_ANSWER) == []


def test_overlap_is_high_for_copied_text_and_low_for_new_ideas():
    src = [CORPUS["reranking"]]
    assert overlap_score("Reranking reorders retrieved documents [reranking].", src) == 1.0
    assert overlap_score("Pinecone costs seventy dollars monthly [reranking].", src) == 0.0


def test_parse_verdict_handles_code_fences_and_junk():
    assert parse_verdict('```json\n{"verdict": "Partial", "reason": "adds a claim"}\n```') == \
        {"verdict": "partial", "reason": "adds a claim"}
    assert parse_verdict("not json at all")["verdict"] == "unparsed"
    assert parse_verdict('{"verdict": "maybe"}')["verdict"] == "unparsed"


def test_judge_sees_only_the_cited_source_without_citation_tags():
    client = FakeJudgeClient('{"verdict": "partial", "reason": "Source says nothing about low recall."}')
    check = check_answer(record("If recall is low, use reranking [reranking]."), CORPUS, ClaudeJudge(client=client))
    sent = client.calls[0]["messages"][0]["content"]
    assert '<source id="reranking">' in sent and "recall_at_k" not in sent
    assert sent.endswith("Claim: If recall is low, use reranking.")
    assert check.claims[0].judge_verdict == "partial"
    assert check.faithfulness == 0.0


def test_uncited_claim_is_unsupported_without_calling_the_judge():
    client = FakeJudgeClient('{"verdict": "supported", "reason": ""}')
    check = check_answer(record("Reranking is magic."), CORPUS, ClaudeJudge(client=client))
    assert client.calls == []
    assert check.claims[0].overlap_verdict == "uncited"
    assert check.claims[0].judge_verdict == "unsupported"


def test_refusals_have_no_claims_and_no_score():
    check = check_answer(record(IDK_ANSWER + " The sources say X [reranking].", refused=True), CORPUS)
    assert check.claims == [] and check.faithfulness is None


def test_faithfulness_is_share_of_supported_claims():
    client = FakeJudgeClient('{"verdict": "supported", "reason": "ok"}')
    check = check_answer(record("Recall counts hits [recall_at_k]. Reranking reorders [reranking]."),
                         CORPUS, ClaudeJudge(client=client))
    assert check.faithfulness == 1.0 and len(client.calls) == 2
