import pytest
from app.modules.claim_extractor import claim_extractor


@pytest.mark.asyncio
async def test_sentence_splitting_with_spans():
    text = "The earth revolves around the sun. The moon revolves around the earth."
    sentences = claim_extractor._split_into_sentences_with_spans(text)
    assert len(sentences) == 2
    assert sentences[0]["text"].startswith("The earth")
    assert sentences[0]["start_char"] == 0
    assert text[sentences[0]["start_char"]:sentences[0]["end_char"]].strip() == sentences[0]["text"]


@pytest.mark.asyncio
async def test_compound_sentence_local_decomposition():
    text = "The treaty was signed in 1905, and it concluded the Russo-Japanese War; however, tensions remained high."
    claims = await claim_extractor.extract_claims(text)
    assert len(claims) >= 2
    for c in claims:
        assert "claim_text" in c
        assert "start_char" in c
        assert "end_char" in c
        assert c["start_char"] >= 0
        assert c["end_char"] <= len(text)


def test_syntactic_complexity_scoring():
    simple_sentence = "The model predicted a high probability."
    complex_sentence = "Although the revenue grew by 25%, the operating cash flow declined sharply; furthermore, customer retention, which had been stable, fell to 78%."
    
    score_simple = claim_extractor._calculate_syntactic_complexity(simple_sentence)
    score_complex = claim_extractor._calculate_syntactic_complexity(complex_sentence)
    
    assert score_simple == 0
    assert score_complex >= 3
