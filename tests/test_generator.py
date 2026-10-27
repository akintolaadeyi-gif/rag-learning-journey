"""Generator tests with a fake Claude client: no API key, no network, no cost."""
from types import SimpleNamespace

from src.generator import (IDK_ANSWER, ClaudeGenerator, build_user_message,
                           is_refusal, parse_citations)

DOCS = [{"id": "bm25", "text": "BM25 ranks by keywords."},
        {"id": "embeddings", "text": "Embeddings capture meaning."}]


class FakeClient:
    def __init__(self, reply):
        self.reply = reply
        self.last_call = None
        self.messages = self

    def create(self, **kwargs):
        self.last_call = kwargs
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text=self.reply)],
            usage=SimpleNamespace(input_tokens=100, output_tokens=20),
        )


def test_sources_are_in_the_prompt_with_ids():
    msg = build_user_message("What is BM25?", DOCS)
    assert '<source id="bm25">BM25 ranks by keywords.</source>' in msg
    assert "Question: What is BM25?" in msg


def test_parse_citations_dedupes_in_order():
    assert parse_citations("A [bm25]. B [embeddings]. C [bm25].") == ["bm25", "embeddings"]


def test_valid_answer_is_checked():
    g = ClaudeGenerator(client=FakeClient("BM25 ranks by keywords [bm25].")).generate("q", DOCS)
    assert g.cited_ids == ["bm25"]
    assert g.invalid_citations == []
    assert not g.refused
    assert g.input_tokens == 100


def test_made_up_citation_is_flagged():
    g = ClaudeGenerator(client=FakeClient("It is fast [speed_doc].")).generate("q", DOCS)
    assert g.invalid_citations == ["speed_doc"]


def test_refusal_is_detected():
    assert is_refusal(IDK_ANSWER)
    g = ClaudeGenerator(client=FakeClient(IDK_ANSWER)).generate("q", DOCS)
    assert g.refused and g.cited_ids == []


